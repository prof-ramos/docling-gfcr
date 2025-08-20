#!/usr/bin/env python3
from __future__ import annotations

import logging
import sys
from pathlib import Path

INPUT_PATH = Path("/Users/gabrielramos/docling/manual-de-redacao.pdf")
OUTPUT_DIR = Path("/Users/gabrielramos/docling/output")
OUTPUT_MD = OUTPUT_DIR / "manual-de-redacao.md"
OUTPUT_TXT = OUTPUT_DIR / "manual-de-redacao.txt"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("convert")


def ensure_paths() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {INPUT_PATH}")


def convert_with_docling() -> str | None:
    try:
        from docling.document_converter import DocumentConverter  # type: ignore
    except Exception as e:
        logger.warning("Docling indisponível ou API não encontrada: %s", e)
        return None

    try:
        converter = DocumentConverter()
        result = converter.convert(str(INPUT_PATH))
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


def fallback_with_pymupdf() -> str:
    import fitz  # PyMuPDF

    doc = fitz.open(str(INPUT_PATH))
    parts: list[str] = []
    for page_index in range(len(doc)):
        page = doc.load_page(page_index)
        text = page.get_text()
        parts.append(f"\n\n# Página {page_index + 1}\n\n{text}")
    doc.close()
    return "\n".join(parts)


def main() -> int:
    try:
        ensure_paths()
        logger.info("Convertendo PDF: %s", INPUT_PATH)

        markdown = convert_with_docling()
        if markdown is not None and markdown.strip():
            OUTPUT_MD.write_text(markdown, encoding="utf-8")
            logger.info("Markdown gerado: %s", OUTPUT_MD)
            return 0

        logger.info("Usando fallback PyMuPDF para extrair texto...")
        text_content = fallback_with_pymupdf()
        OUTPUT_TXT.write_text(text_content, encoding="utf-8")
        logger.info("Texto extraído (fallback) salvo em: %s", OUTPUT_TXT)
        return 0
    except Exception as e:
        logger.error("Erro na conversão: %s", e, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
