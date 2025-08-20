#!/usr/bin/env python3
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
import argparse
import json
from typing import Dict, Optional

# Configurar logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Configurações via environment variables
DEFAULT_OUTPUT_DIR = os.getenv("DOCLING_OUTPUT_DIR", "/Users/gabrielramos/docling/output")


def ensure_paths(input_path: Path, output_dir: Path) -> tuple[Path, Path]:
    """Garante diretório de saída e retorna caminhos de saída padrão.

    Retorna os caminhos de saída para Markdown e Texto (fallback), baseados no nome do arquivo de entrada.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    if not input_path.exists():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {input_path}")
    output_md = output_dir / f"{input_path.stem}.md"
    output_txt = output_dir / f"{input_path.stem}.txt"
    return output_md, output_txt


def convert_with_docling(input_path: Path) -> str | None:
    try:
        from docling.document_converter import DocumentConverter  # type: ignore
    except Exception as e:
        logger.warning("Docling indisponível ou API não encontrada: %s", e)
        return None

    try:
        converter = DocumentConverter()
        result = converter.convert(str(input_path))
        # Algumas versões expõem .document.export_to_markdown();
        # outras podem usar métodos utilitários diferentes.
        if hasattr(result, "document") and hasattr(result.document, "export_to_markdown"):
            markdown_content = result.document.export_to_markdown()
            return markdown_content  # type: ignore[return-value]
        logger.warning("API do Docling não possui export_to_markdown nesta instalação.")
        return None
    except Exception as e:
        logger.error("Falha convertendo com Docling: %s", e, exc_info=True)
        return None


def fallback_with_pymupdf(input_path: Path) -> str:
    import fitz  # PyMuPDF

    doc = fitz.open(str(input_path))
    parts: list[str] = []
    for page_index in range(len(doc)):
        page = doc.load_page(page_index)
        text = page.get_text()
        parts.append(f"\n\n# Página {page_index + 1}\n\n{text}")
    doc.close()
    return "\n".join(parts)


def convert_document(
    input_path: str, 
    output_dir: Optional[str] = None,
    return_content: bool = False
) -> Dict[str, any]:
    """
    Função principal de conversão reutilizável.
    
    Args:
        input_path: Caminho para arquivo de entrada
        output_dir: Diretório de saída (usa padrão se None)
        return_content: Se deve incluir conteúdo na resposta
        
    Returns:
        Dict com informações do resultado da conversão
    """
    try:
        input_path_obj = Path(input_path).expanduser().resolve()
        output_dir_obj = Path(output_dir or DEFAULT_OUTPUT_DIR).expanduser().resolve()
        
        output_md, output_txt = ensure_paths(input_path_obj, output_dir_obj)
        logger.info("Convertendo PDF: %s", input_path_obj)

        result = {
            "success": True,
            "method": None,
            "output_file": None,
            "file_size_bytes": 0
        }
        
        markdown = convert_with_docling(input_path_obj)
        if markdown is not None and markdown.strip():
            output_md.write_text(markdown, encoding="utf-8")
            logger.info("Markdown gerado: %s", output_md)
            result.update({
                "method": "docling",
                "output_file": str(output_md),
                "file_size_bytes": output_md.stat().st_size
            })
            if return_content:
                result["content"] = markdown
        else:
            logger.info("Usando fallback PyMuPDF para extrair texto...")
            text_content = fallback_with_pymupdf(input_path_obj)
            output_txt.write_text(text_content, encoding="utf-8")
            logger.info("Texto extraído (fallback) salvo em: %s", output_txt)
            result.update({
                "method": "pymupdf",
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
        parser.add_argument("-i", "--input", required=True, help="Caminho absoluto do arquivo a ser convertido (ex.: /abs/path/file.pdf)")
        parser.add_argument("-o", "--output-dir", default="", help="Diretório de saída. Ignorado: saída fixa em /Users/gabrielramos/docling/output")
        parser.add_argument("--json", action="store_true", help="Retorna resultado em formato JSON")
        args = parser.parse_args()

        input_path = args.input
        # Saída fixa conforme especificado
        output_dir = "/Users/gabrielramos/docling/output"

        result = convert_document(input_path, output_dir)
        
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
