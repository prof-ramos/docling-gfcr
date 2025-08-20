from __future__ import annotations

import sys
import types
from pathlib import Path
import pytest

# Garantir que o diretório do projeto esteja no sys.path para importar 'scripts'
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import scripts.convert as conv  # noqa: E402


def test_ensure_paths_missing_input(tmp_path: Path):
    out = tmp_path / "out"
    with pytest.raises(FileNotFoundError):
        conv.ensure_paths(tmp_path / "nope.pdf", out)


def test_ensure_paths_creates_outputs(tmp_path: Path):
    inpdf = tmp_path / "file.pdf"
    inpdf.write_bytes(b"%PDF-1.4\n")
    outdir = tmp_path / "o"
    md, txt = conv.ensure_paths(inpdf, outdir)
    assert md.name == "file.md"
    assert txt.name == "file.txt"
    assert outdir.exists()


def test_convert_with_docling_success(tmp_path: Path, monkeypatch):
    inpdf = tmp_path / "a.pdf"
    inpdf.write_bytes(b"%PDF-1.4\n")

    class FakeDoc:
        def export_to_markdown(self):
            return "# ok"

    class FakeRes:
        document = FakeDoc()

    class FakeConverter:
        def convert(self, s: str):
            assert s == str(inpdf)
            return FakeRes()

    # Simular módulo docling.document_converter
    fake_mod = types.SimpleNamespace(DocumentConverter=FakeConverter)
    sys.modules["docling.document_converter"] = fake_mod

    md = conv.convert_with_docling(inpdf)
    assert md.strip() == "# ok"


def test_convert_with_docling_missing_api(tmp_path: Path):
    inpdf = tmp_path / "a.pdf"
    inpdf.write_bytes(b"%PDF-1.4\n")

    # Remover módulo para simular indisponibilidade
    sys.modules.pop("docling.document_converter", None)

    md = conv.convert_with_docling(inpdf)
    assert md is None


def test_fallback_with_pymupdf(tmp_path: Path, monkeypatch):
    inpdf = tmp_path / "b.pdf"
    inpdf.write_bytes(b"%PDF-1.4\n")

    class FakePage:
        def get_text(self) -> str:
            return "hello"

    class FakeDoc:
        def __len__(self) -> int:
            return 2

        def load_page(self, i: int):
            assert i in (0, 1)
            return FakePage()

        def close(self) -> None:
            pass

    monkeypatch.setitem(sys.modules, "fitz", types.SimpleNamespace(open=lambda p: FakeDoc()))

    text = conv.fallback_with_pymupdf(inpdf)
    assert "hello" in text
    assert "Página 1" in text
    assert "Página 2" in text
