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

from .convert import convert_document, SUPPORTED_EXTENSIONS


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
            },
            "enhance_with_openai": {
                "type": "boolean",
                "description": "Se true, usa OpenAI para melhorar o resultado (requer OPENAI_API_KEY no ambiente)",
                "default": False
            }
        },
        "required": ["input_path"]
    }
}


def convert_document_tool(
    input_path: str, 
    output_dir: str = "/Users/gabrielramos/docling/output",
    return_content: bool = False,
    enhance_with_openai: bool = False
) -> Dict[str, Any]:
    """
    Interface de tool para conversão de documentos.
    
    Args:
        input_path: Caminho absoluto para o arquivo a ser convertido
        output_dir: Diretório de saída (padrão: /Users/gabrielramos/docling/output)
        return_content: Se deve retornar o conteúdo na resposta
        enhance_with_openai: Se deve usar OpenAI para melhorar o resultado
        
    Returns:
        Dict com status da conversão e informações do arquivo de saída
    """
    try:
        # Usar a nova função convert_document que já tem todas as funcionalidades
        result = convert_document(
            input_path=input_path,
            output_dir=output_dir,
            return_content=return_content,
            enhance_with_openai=enhance_with_openai
        )
        
        # Adicionar informações extras para compatibilidade com tool interface
        if result.get("success"):
            result["input_path"] = str(Path(input_path).expanduser().resolve())
            result["output_dir"] = str(Path(output_dir).expanduser().resolve())
            result["conversion_method"] = result.get("method", "unknown")
        
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
            enhance_with_openai = input_data.get("enhance_with_openai", False)
            result = convert_document_tool(input_path, output_dir, return_content, enhance_with_openai)
        
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