#!/usr/bin/env python3
"""
Agente especializado para conversão de documentos para Markdown.

Este agente oferece funcionalidades avançadas de conversão focadas na
qualidade e formatação do output Markdown, incluindo processamento de
metadados, otimização de estrutura e validação do resultado.
"""
from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, TypedDict, Union
import re
from jsonschema import validate, ValidationError

try:
    from .convert import convert_with_docling, fallback_with_pymupdf, ensure_paths
except ImportError:
    # Fallback para quando executado diretamente
    import sys
    from pathlib import Path
    
    # Adicionar diretório scripts ao path para imports
    sys.path.insert(0, str(Path(__file__).parent))
    from convert import convert_with_docling, fallback_with_pymupdf, ensure_paths


# Configurar logging específico do agente
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(
        "%(asctime)s [%(name)s] %(levelname)s %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Configurações via environment variables
DEFAULT_OUTPUT_DIR = os.getenv(
    "DOCLING_OUTPUT_DIR", 
    "/Users/gabrielramos/docling/output"
)


class DocumentAnalysis(TypedDict):
    """Resultado da análise de documento."""
    filename: str
    size_bytes: int
    size_mb: float
    extension: str
    is_supported: bool
    estimated_pages: int


class ValidationMetrics(TypedDict):
    """Métricas de validação de qualidade."""
    headers_count: int
    paragraphs_count: int
    lists_count: int
    word_count: int
    char_count: int


class ValidationResult(TypedDict):
    """Resultado da validação de qualidade."""
    valid: bool
    issues: List[str]
    metrics: ValidationMetrics
    quality_score: int


class ConversionResult(TypedDict):
    """Resultado da conversão de documento."""
    success: bool
    agent: str
    input_analysis: Optional[DocumentAnalysis]
    conversion_method: Optional[str]
    output_file: Optional[str]
    file_size_bytes: Optional[int]
    optimized: bool
    validated: bool
    validation: Optional[ValidationResult]
    content: Optional[str]
    error: Optional[str]


class BatchResult(TypedDict):
    """Resultado da conversão em lote."""
    success: bool
    batch: bool
    results: List[ConversionResult]
    summary: Dict[str, int]


# Schema JSON para validação de entrada
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "input_path": {
            "oneOf": [
                {"type": "string", "minLength": 1},
                {
                    "type": "array",
                    "items": {"type": "string", "minLength": 1},
                    "minItems": 1
                }
            ]
        },
        "output_dir": {"type": "string", "minLength": 1},
        "optimize": {"type": "boolean"},
        "validate": {"type": "boolean"},
        "return_content": {"type": "boolean"}
    },
    "required": ["input_path"],
    "additionalProperties": False
}


class MarkdownAgent:
    """
    Agente especializado em conversão para Markdown com funcionalidades avançadas.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)
        self.supported_formats = ['.pdf', '.docx', '.doc', '.txt']
        
    def analyze_document(self, file_path: Path) -> Union[DocumentAnalysis, Dict[str, str]]:
        """
        Analisa o documento antes da conversão.
        
        Args:
            file_path: Caminho para o arquivo
            
        Returns:
            DocumentAnalysis com metadados ou dict com erro
        """
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
                
            stat = file_path.stat()
            extension = file_path.suffix.lower()
            
            return DocumentAnalysis(
                filename=file_path.name,
                size_bytes=stat.st_size,
                size_mb=round(stat.st_size / (1024 * 1024), 2),
                extension=extension,
                is_supported=extension in self.supported_formats,
                estimated_pages=max(1, stat.st_size // 2048) if extension == '.pdf' else 1
            )
        except (OSError, FileNotFoundError) as e:
            logger.warning(f"Erro ao analisar documento: {e}")
            return {"error": str(e)}

    def optimize_markdown(self, content: str, filename: str) -> str:
        """
        Otimiza o conteúdo Markdown para melhor legibilidade.
        
        Args:
            content: Conteúdo Markdown bruto
            filename: Nome do arquivo original
            
        Returns:
            Conteúdo Markdown otimizado
        """
        if not content or not content.strip():
            return content
            
        # Adicionar metadados do documento
        metadata = f"""---
title: {Path(filename).stem}
source: {filename}
converted_by: Docling Markdown Agent
---

"""
        
        # Limpar múltiplas quebras de linha
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Garantir espaçamento adequado após cabeçalhos
        content = re.sub(r'(#{1,6}[^\n]*)\n([^\n#])', r'\1\n\n\2', content)
        
        # Melhorar formatação de listas
        content = re.sub(r'\n(\s*[-*+])', r'\n\n\1', content)
        content = re.sub(r'(\n\s*[-*+][^\n]*)\n([^\s\-*+\n])', r'\1\n\n\2', content)
        
        # Garantir quebra de linha no final
        if not content.endswith('\n'):
            content += '\n'
            
        return metadata + content

    def validate_markdown(self, content: str) -> ValidationResult:
        """
        Valida a qualidade do Markdown gerado.
        
        Args:
            content: Conteúdo Markdown
            
        Returns:
            ValidationResult com métricas de qualidade
        """
        if not content:
            return ValidationResult(
                valid=False,
                issues=["Conteúdo vazio"],
                metrics=ValidationMetrics(
                    headers_count=0,
                    paragraphs_count=0,
                    lists_count=0,
                    word_count=0,
                    char_count=0
                ),
                quality_score=0
            )
            
        issues: List[str] = []
        
        # Contar elementos estruturais
        headers = re.findall(r'^#{1,6}\s+.+', content, re.MULTILINE)
        paragraphs = re.findall(r'^[^#\n-*+\s][^\n]*$', content, re.MULTILINE)
        lists = re.findall(r'^\s*[-*+]\s+', content, re.MULTILINE)
        
        metrics = ValidationMetrics(
            headers_count=len(headers),
            paragraphs_count=len(paragraphs),
            lists_count=len(lists),
            word_count=len(content.split()),
            char_count=len(content)
        )
        
        # Validações básicas
        if not headers:
            issues.append("Nenhum cabeçalho encontrado")
            
        if len(paragraphs) < 2 and len(content) > 100:
            issues.append("Poucos parágrafos para o tamanho do documento")
            
        if metrics["word_count"] < 10:
            issues.append("Conteúdo muito curto")
            
        # Verificar formatação
        if '# Página' in content:
            issues.append("Contém marcadores de página do fallback")
            
        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues,
            metrics=metrics,
            quality_score=max(0, 100 - len(issues) * 20)
        )

    def convert_document(
        self, 
        input_path: str,
        output_dir: Optional[str] = None,
        optimize: bool = True,
        validate: bool = True,
        return_content: bool = False
    ) -> ConversionResult:
        """
        Converte documento para Markdown com funcionalidades avançadas do agente.
        
        Args:
            input_path: Caminho do arquivo de entrada
            output_dir: Diretório de saída (opcional)
            optimize: Se deve otimizar o Markdown
            validate: Se deve validar a qualidade
            return_content: Se deve retornar o conteúdo
            
        Returns:
            Dict com resultado da conversão e análises
        """
        try:
            input_path_obj = Path(input_path).expanduser().resolve()
            if not input_path_obj.exists():
                return ConversionResult(
                    success=False,
                    agent="markdown_agent",
                    input_analysis=None,
                    conversion_method=None,
                    output_file=None,
                    file_size_bytes=None,
                    optimized=False,
                    validated=False,
                    validation=None,
                    content=None,
                    error=f"Arquivo não encontrado: {input_path}"
                )
                
            # Análise prévia do documento
            doc_analysis_result = self.analyze_document(input_path_obj)
            if "error" in doc_analysis_result:
                return ConversionResult(
                    success=False,
                    agent="markdown_agent",
                    input_analysis=None,
                    conversion_method=None,
                    output_file=None,
                    file_size_bytes=None,
                    optimized=False,
                    validated=False,
                    validation=None,
                    content=None,
                    error=doc_analysis_result["error"]
                )
                
            doc_analysis = doc_analysis_result  # type: ignore
            if not doc_analysis["is_supported"]:
                return ConversionResult(
                    success=False,
                    agent="markdown_agent",
                    input_analysis=doc_analysis,
                    conversion_method=None,
                    output_file=None,
                    file_size_bytes=None,
                    optimized=False,
                    validated=False,
                    validation=None,
                    content=None,
                    error=f"Formato não suportado: {doc_analysis['extension']}"
                )

            # Definir diretório de saída
            output_dir_obj = Path(output_dir or self.output_dir).expanduser().resolve()
            output_md, output_txt = ensure_paths(input_path_obj, output_dir_obj)
            
            logger.info(f"Convertendo documento: {input_path_obj}")
            logger.info(f"Análise: {doc_analysis['size_mb']}MB, ~{doc_analysis['estimated_pages']} páginas")
            
            # Conversão principal
            markdown_content = convert_with_docling(input_path_obj)
            conversion_method = "docling"
            output_file = output_md
            
            # Fallback se necessário
            if not markdown_content or not markdown_content.strip():
                logger.info("Usando fallback PyMuPDF...")
                text_content = fallback_with_pymupdf(input_path_obj)
                markdown_content = f"# {input_path_obj.stem}\n\n{text_content}"
                conversion_method = "pymupdf_fallback"
                output_file = output_txt
                
            # Otimização do Markdown
            if optimize and markdown_content:
                logger.info("Otimizando Markdown...")
                original_length = len(markdown_content)
                markdown_content = self.optimize_markdown(markdown_content, input_path_obj.name)
                logger.info(f"Otimização: {original_length} → {len(markdown_content)} chars")
                
            # Validação da qualidade
            validation_result = {}
            if validate and markdown_content:
                logger.info("Validando qualidade do Markdown...")
                validation_result = self.validate_markdown(markdown_content)
                logger.info(f"Qualidade: {validation_result['quality_score']}/100")
                
            # Salvar arquivo
            if markdown_content:
                output_file.write_text(markdown_content, encoding="utf-8")
                logger.info(f"Markdown salvo: {output_file}")
                
            # Resultado estruturado
            result = {
                "success": True,
                "agent": "markdown_agent",
                "input_analysis": doc_analysis,
                "conversion_method": conversion_method,
                "output_file": str(output_file),
                "file_size_bytes": output_file.stat().st_size if output_file.exists() else 0,
                "optimized": optimize,
                "validated": validate
            }
            
            if validation_result:
                result["validation"] = validation_result
                
            if return_content:
                result["content"] = markdown_content
                
            return result
            
        except Exception as e:
            logger.error(f"Erro na conversão: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "agent": "markdown_agent"
            }

    def batch_convert(self, input_paths: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Converte múltiplos documentos em lote.
        
        Args:
            input_paths: Lista de caminhos de arquivos
            **kwargs: Parâmetros para convert_document
            
        Returns:
            Lista com resultados de cada conversão
        """
        results = []
        logger.info(f"Iniciando conversão em lote de {len(input_paths)} arquivos")
        
        for i, path in enumerate(input_paths, 1):
            logger.info(f"Processando arquivo {i}/{len(input_paths)}: {path}")
            result = self.convert_document(path, **kwargs)
            results.append(result)
            
            if result["success"]:
                logger.info(f"✓ Sucesso: {path}")
            else:
                logger.error(f"✗ Falha: {path} - {result.get('error', 'Erro desconhecido')}")
                
        success_count = sum(1 for r in results if r["success"])
        logger.info(f"Lote finalizado: {success_count}/{len(input_paths)} sucessos")
        
        return results


def main():
    """
    Entry point para uso como ferramenta independente.
    Lê configuração JSON do stdin e retorna resultado no stdout.
    """
    try:
        # Ler e validar JSON de entrada
        input_json = sys.stdin.read()
        if not input_json.strip():
            raise ValueError("Entrada JSON vazia")
            
        input_data = json.loads(input_json)
        
        # Validar schema
        try:
            validate(instance=input_data, schema=INPUT_SCHEMA)
        except ValidationError as e:
            raise ValueError(f"Schema JSON inválido: {e.message}")
        
        # Extrair parâmetros
        input_path = input_data["input_path"]
            
        # Parâmetros opcionais
        output_dir = input_data.get("output_dir")
        optimize = input_data.get("optimize", True)
        validate_quality = input_data.get("validate", True)
        return_content = input_data.get("return_content", False)
        
        # Verificar se é conversão em lote
        if isinstance(input_path, list):
            agent = MarkdownAgent(output_dir or "/Users/gabrielramos/docling/output")
            results = agent.batch_convert(
                input_path, 
                output_dir=output_dir,
                optimize=optimize,
                validate=validate_quality,
                return_content=return_content
            )
            result = {
                "success": True,
                "batch": True,
                "results": results,
                "summary": {
                    "total": len(results),
                    "success": sum(1 for r in results if r["success"]),
                    "failed": sum(1 for r in results if not r["success"])
                }
            }
        else:
            # Conversão única
            agent = MarkdownAgent(output_dir)
            result = agent.convert_document(
                input_path, 
                output_dir,
                optimize,
                validate_quality,
                return_content
            )
            
        # Retornar resultado JSON
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except json.JSONDecodeError as e:
        error_result = {
            "success": False,
            "error": f"Erro ao decodificar JSON: {str(e)}",
            "agent": "markdown_agent"
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Erro inesperado: {str(e)}",
            "agent": "markdown_agent"
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()