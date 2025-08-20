from __future__ import annotations

import sys
from pathlib import Path
import logging
import types
import pytest

# garantir import do projeto
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import scripts.convert as conv  # noqa: E402


def test_cli_requires_input(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["convert.py"])  # sem --input
    with pytest.raises(SystemExit) as ex:
        conv.main()
    assert ex.value.code == 2  # argparse usage error


def test_cli_writes_md_when_docling_ok(tmp_path, monkeypatch, caplog):
    inpdf = tmp_path / "doc.pdf"
    inpdf.write_bytes(b"%PDF-1.4\n")
    outdir = tmp_path / "out"

    # evitar processamento pesado
    monkeypatch.setattr(conv, "convert_with_docling", lambda p: "# md")
    monkeypatch.setattr(conv, "fallback_with_pymupdf", lambda p: "TXT")

    argv = [
        "convert.py",
        "--input",
        str(inpdf),
        "--output-dir",
        str(outdir),
    ]
    monkeypatch.setattr(sys, "argv", argv)

    caplog.clear()
    caplog.set_level(logging.INFO, logger="convert")
    rc = conv.main()
    assert rc == 0

    md_file = Path("/Users/gabrielramos/docling/output") / "doc.md"
    assert md_file.exists()
    assert "Markdown gerado" in " ".join(m for _, _, m in caplog.record_tuples)


def test_cli_fallback_when_docling_empty(tmp_path, monkeypatch, caplog):
    inpdf = tmp_path / "doc.pdf"
    inpdf.write_bytes(b"%PDF-1.4\n")
    outdir = tmp_path / "out"

    # Docling retorna vazio, força fallback
    monkeypatch.setattr(conv, "convert_with_docling", lambda p: "   ")
    monkeypatch.setattr(conv, "fallback_with_pymupdf", lambda p: "content")

    argv = [
        "convert.py",
        "--input",
        str(inpdf),
        "--output-dir",
        str(outdir),
    ]
    monkeypatch.setattr(sys, "argv", argv)

    caplog.clear()
    caplog.set_level(logging.INFO, logger="convert")
    rc = conv.main()
    assert rc == 0

    txt_file = Path("/Users/gabrielramos/docling/output") / "doc.txt"
    assert txt_file.exists()
    # confere log de fallback
    assert any("fallback" in m for _, _, m in caplog.record_tuples)
