#!/usr/bin/env python3
"""
Claude Code Tool Interface para conversão de documentos.

Este módulo fornece uma interface para que agentes do Claude Code
possam usar o sistema de conversão de documentos como uma tool.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

from .convert import convert_with_docling, fallback_with_pymupdf, get_generic_fallback, ensure_paths, SUPPORTED_EXTENSIONS, FALLBACK_EXTENSIONS


# JSON Schema para o tool do Claude Code
TOOL_SCHEMA = {
    "name": "convert_document",
    "description": "Converte documentos (PDF, DOCX, XLSX, PPTX, HTML, imagens, etc.) para Markdown usando Docling",
    "input_schema": {
        "type": "object",
        "properties": {
            "input_path": {
                "type": "string",
                "description": "Caminho absoluto para o arquivo a ser convertido. Extensões suportadas: " + ", ".join(sorted(SUPPORTED_EXTENSIONS))
            },
            "output_dir": {
                "type": "string", 
                "description": "Diretório de saída (opcional). Se não especificado, usa /Users/gabrielramos/docling/output",
                "default": "/Users/gabrielramos/docling/output"
            },
            "return_content": {
                "type": "boolean",
                "description": "Se true, retorna o conteúdo convertido na resposta. Se false, apenas salva no arquivo",
                "default": False
            }
        },
        "required": ["input_path"]
    }
}


def convert_document_tool(
    input_path: str, 
    output_dir: str = "/Users/gabrielramos/docling/output",
    return_content: bool = False
) -> Dict[str, Any]:
    """
    Interface de tool para conversão de documentos.
    
    Args:
        input_path: Caminho absoluto para o arquivo a ser convertido
        output_dir: Diretório de saída (padrão: /Users/gabrielramos/docling/output)
        return_content: Se deve retornar o conteúdo na resposta
        
    Returns:
        Dict com status da conversão e informações do arquivo de saída
    """
    try:
        input_path_obj = Path(input_path).expanduser().resolve()
        output_dir_obj = Path(output_dir).expanduser().resolve()
        
        # Verificar se arquivo de entrada existe
        if not input_path_obj.exists():
            return {
                "success": False,
                "error": f"Arquivo de entrada não encontrado: {input_path}",
                "input_path": str(input_path_obj),
                "output_dir": str(output_dir_obj)
            }
        
        # Preparar caminhos de saída
        output_md, output_txt = ensure_paths(input_path_obj, output_dir_obj)
        
        # Tentar conversão com Docling primeiro
        markdown_content = convert_with_docling(input_path_obj)
        
        result = {
            "success": True,
            "input_path": str(input_path_obj),
            "output_dir": str(output_dir_obj),
            "conversion_method": None,
            "output_file": None,
            "file_size_bytes": None
        }
        
        if markdown_content is not None and markdown_content.strip():
            # Sucesso com Docling
            output_md.write_text(markdown_content, encoding="utf-8")
            result.update({
                "conversion_method": "docling",
                "output_file": str(output_md),
                "file_size_bytes": output_md.stat().st_size
            })
            
            if return_content:
                result["content"] = markdown_content
                
        else:
            # Usar fallback apropriado baseado na extensão
            extension = input_path_obj.suffix.lower()
            if extension in FALLBACK_EXTENSIONS:
                text_content = fallback_with_pymupdf(input_path_obj)
                fallback_method = "pymupdf_fallback"
            else:
                text_content = get_generic_fallback(input_path_obj)
                fallback_method = "generic_fallback"
                
            output_txt.write_text(text_content, encoding="utf-8")
            result.update({
                "conversion_method": fallback_method,
                "output_file": str(output_txt),
                "file_size_bytes": output_txt.stat().st_size
            })
            
            if return_content:
                result["content"] = text_content
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro durante conversão: {str(e)}",
            "input_path": input_path,
            "output_dir": output_dir
        }


def main():
    """
    Entry point para uso como tool do Claude Code.
    
    Lê parâmetros JSON do stdin e retorna resultado JSON no stdout.
    """
    try:
        # Ler entrada JSON do stdin
        input_data = json.loads(sys.stdin.read())
        
        # Extrair parâmetros
        input_path = input_data.get("input_path")
        output_dir = input_data.get("output_dir", "/Users/gabrielramos/docling/output")
        return_content = input_data.get("return_content", False)
        
        if not input_path:
            result = {
                "success": False,
                "error": "Parâmetro 'input_path' é obrigatório"
            }
        else:
            # Executar conversão
            result = convert_document_tool(input_path, output_dir, return_content)
        
        # Retornar resultado JSON
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except json.JSONDecodeError as e:
        error_result = {
            "success": False,
            "error": f"Erro ao decodificar JSON de entrada: {str(e)}"
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)
        
    except Exception as e:
        error_result = {
            "success": False, 
            "error": f"Erro inesperado: {str(e)}"
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()