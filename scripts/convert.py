#!/usr/bin/env python3
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
import argparse
import json
from typing import Dict, Optional, List

# Configurar logging primeiro
logger = logging.getLogger(__name__)

try:
    from .openai_enhancer import OpenAIEnhancer, create_enhancer_from_env
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI não disponível. Funcionalidades de enriquecimento desabilitadas.")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Configurações via environment variables
DEFAULT_OUTPUT_DIR = os.getenv("DOCLING_OUTPUT_DIR", "/Users/gabrielramos/docling/output")

# Extensões suportadas pelo Docling
SUPPORTED_EXTENSIONS = {
    # Documentos
    '.pdf', '.docx', '.xlsx', '.pptx', '.html', '.xhtml', '.md', '.csv',
    # Imagens  
    '.png', '.jpeg', '.jpg', '.tiff', '.tif', '.bmp', '.webp',
    # Formatos especializados
    '.xml', '.json',
    # AsciiDoc
    '.adoc', '.asciidoc'
}

# Extensões que precisam de fallback (apenas PDF por enquanto)
FALLBACK_EXTENSIONS = {'.pdf'}


def validate_input_file(input_path: Path) -> None:
    """Valida se o arquivo de entrada existe e é suportado."""
    if not input_path.exists():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {input_path}")
    
    extension = input_path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        supported_list = ', '.join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(
            f"Extensão '{extension}' não suportada. "
            f"Extensões suportadas: {supported_list}"
        )


def ensure_paths(input_path: Path, output_dir: Path) -> tuple[Path, Path]:
    """Garante diretório de saída e retorna caminhos de saída padrão.

    Retorna os caminhos de saída para Markdown e Texto (fallback), baseados no nome do arquivo de entrada.
    Substitui espaços por underline nos nomes de arquivo de saída.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    validate_input_file(input_path)
    # Substituir espaços por underline no nome do arquivo de saída
    clean_stem = input_path.stem.replace(" ", "_")
    output_md = output_dir / f"{clean_stem}.md"
    output_txt = output_dir / f"{clean_stem}.txt"
    return output_md, output_txt


def convert_with_docling(input_path: Path) -> str | None:
    """Converte documento usando Docling para todas as extensões suportadas."""
    try:
        from docling.document_converter import DocumentConverter  # type: ignore
    except Exception as e:
        logger.warning("Docling indisponível ou API não encontrada: %s", e)
        return None

    try:
        # Configurar converter para diferentes tipos de arquivo
        converter = DocumentConverter()
        
        extension = input_path.suffix.lower()
        logger.info(f"Processando arquivo {extension}: {input_path.name}")
        
        result = converter.convert(str(input_path))
        
        # Tentar diferentes métodos de exportação conforme versão do Docling
        if hasattr(result, "document"):
            doc = result.document
            if hasattr(doc, "export_to_markdown"):
                markdown_content = doc.export_to_markdown()
                return markdown_content  # type: ignore[return-value]
            elif hasattr(doc, "export_to_markdown_str"):
                markdown_content = doc.export_to_markdown_str()
                return markdown_content  # type: ignore[return-value]
            elif hasattr(doc, "to_markdown"):
                markdown_content = doc.to_markdown()
                return markdown_content  # type: ignore[return-value]
        
        logger.warning("API do Docling não possui método de exportação Markdown conhecido nesta instalação.")
        return None
    except Exception as e:
        logger.error(f"Falha convertendo {extension} com Docling: %s", e, exc_info=True)
        return None


def fallback_with_pymupdf(input_path: Path) -> str:
    """Fallback usando PyMuPDF apenas para PDFs."""
    extension = input_path.suffix.lower()
    if extension != '.pdf':
        raise ValueError(f"PyMuPDF fallback só suporta PDF, não {extension}")
        
    import fitz  # PyMuPDF

    doc = fitz.open(str(input_path))
    parts: list[str] = []
    for page_index in range(len(doc)):
        page = doc.load_page(page_index)
        text = page.get_text()
        parts.append(f"\n\n# Página {page_index + 1}\n\n{text}")
    doc.close()
    return "\n".join(parts)


def get_generic_fallback(input_path: Path) -> str:
    """Fallback genérico para arquivos de texto simples."""
    extension = input_path.suffix.lower()
    
    # Para arquivos de texto simples, apenas lemos o conteúdo
    text_extensions = {'.md', '.html', '.xhtml', '.csv', '.xml', '.json', '.adoc', '.asciidoc'}
    
    if extension in text_extensions:
        try:
            content = input_path.read_text(encoding='utf-8')
            return f"# {input_path.name}\n\n{content}"
        except UnicodeDecodeError:
            # Tentar outras codificações
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    content = input_path.read_text(encoding=encoding)
                    return f"# {input_path.name}\n\n{content}"
                except UnicodeDecodeError:
                    continue
    
    # Para outros tipos, retornar mensagem explicativa
    return f"# {input_path.name}\n\nArquivo {extension} não pôde ser processado. Formato não suportado para fallback."


def convert_document(
    input_path: str, 
    output_dir: Optional[str] = None,
    return_content: bool = False,
    enhance_with_openai: bool = False
) -> Dict[str, any]:
    """
    Função principal de conversão reutilizável.
    
    Args:
        input_path: Caminho para arquivo de entrada
        output_dir: Diretório de saída (usa padrão se None)
        return_content: Se deve incluir conteúdo na resposta
        enhance_with_openai: Se deve usar OpenAI para melhorar o resultado
        
    Returns:
        Dict com informações do resultado da conversão
    """
    try:
        input_path_obj = Path(input_path).expanduser().resolve()
        output_dir_obj = Path(output_dir or DEFAULT_OUTPUT_DIR).expanduser().resolve()
        
        output_md, output_txt = ensure_paths(input_path_obj, output_dir_obj)
        extension = input_path_obj.suffix.lower()
        logger.info(f"Convertendo {extension}: %s", input_path_obj)

        result = {
            "success": True,
            "method": None,
            "output_file": None,
            "file_size_bytes": 0
        }
        
        markdown = convert_with_docling(input_path_obj)
        if markdown is not None and markdown.strip():
            # Aplicar enriquecimento OpenAI se solicitado
            if enhance_with_openai and OPENAI_AVAILABLE:
                logger.info("Aplicando enriquecimento OpenAI ao Markdown...")
                try:
                    enhancer = create_enhancer_from_env()
                    enhancement_result = enhancer.enhance_markdown(markdown)
                    
                    if "enhanced_markdown" in enhancement_result:
                        markdown = enhancement_result["enhanced_markdown"]
                        result["openai_enhancement"] = {
                            "applied": True,
                            "metadata": enhancement_result.get("metadata", {}),
                            "improvements": enhancement_result.get("improvements", [])
                        }
                        logger.info("Enriquecimento OpenAI aplicado com sucesso")
                    else:
                        result["openai_enhancement"] = {"applied": False, "error": "Resposta inválida"}
                        
                except Exception as e:
                    logger.warning(f"Erro no enriquecimento OpenAI: {e}")
                    result["openai_enhancement"] = {"applied": False, "error": str(e)}
                    
            output_md.write_text(markdown, encoding="utf-8")
            logger.info("Markdown gerado: %s", output_md)
            result.update({
                "method": "docling" + ("+openai" if enhance_with_openai and OPENAI_AVAILABLE else ""),
                "output_file": str(output_md),
                "file_size_bytes": output_md.stat().st_size
            })
            if return_content:
                result["content"] = markdown
        else:
            extension = input_path_obj.suffix.lower()
            if extension in FALLBACK_EXTENSIONS:
                logger.info("Usando fallback PyMuPDF para extrair texto...")
                text_content = fallback_with_pymupdf(input_path_obj)
                fallback_method = "pymupdf"
            else:
                logger.info(f"Usando fallback genérico para {extension}...")
                text_content = get_generic_fallback(input_path_obj)
                fallback_method = "generic"
                
            output_txt.write_text(text_content, encoding="utf-8")
            logger.info("Conteúdo extraído (fallback) salvo em: %s", output_txt)
            result.update({
                "method": fallback_method,
                "output_file": str(output_txt),
                "file_size_bytes": output_txt.stat().st_size
            })
            if return_content:
                result["content"] = text_content
                
        return result
    except Exception as e:
        logger.error("Erro na conversão: %s", e, exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


def main() -> int:
    try:
        parser = argparse.ArgumentParser(description="Converter documentos para Markdown usando Docling")
        supported_exts = ', '.join(sorted(SUPPORTED_EXTENSIONS))
        parser.add_argument("-i", "--input", required=True, 
                          help=f"Caminho absoluto do arquivo a ser convertido. Extensões suportadas: {supported_exts}")
        parser.add_argument("-o", "--output-dir", default="", help="Diretório de saída. Ignorado: saída fixa em /Users/gabrielramos/docling/output")
        parser.add_argument("--json", action="store_true", help="Retorna resultado em formato JSON")
        parser.add_argument("--enhance", action="store_true", help="Usar OpenAI para melhorar o resultado (requer OPENAI_API_KEY)")
        args = parser.parse_args()

        input_path = args.input
        # Saída fixa conforme especificado
        output_dir = "/Users/gabrielramos/docling/output"

        result = convert_document(input_path, output_dir, enhance_with_openai=args.enhance)
        
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        return 0 if result["success"] else 1
    except Exception as e:
        error_result = {"success": False, "error": str(e)}
        logger.error("Erro na conversão: %s", e, exc_info=True)
        if "--json" in sys.argv:
            print(json.dumps(error_result, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
