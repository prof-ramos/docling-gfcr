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


def test_validate_input_file_missing(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        conv.validate_input_file(tmp_path / "nope.pdf")


def test_validate_input_file_unsupported_extension(tmp_path: Path):
    unsupported = tmp_path / "test.xyz"
    unsupported.write_text("content")
    with pytest.raises(ValueError, match="Extensão '.xyz' não suportada"):
        conv.validate_input_file(unsupported)


def test_validate_input_file_supported_extensions(tmp_path: Path):
    # Testar algumas extensões suportadas
    for ext in [".pdf", ".docx", ".html", ".png", ".md"]:
        test_file = tmp_path / f"test{ext}"
        test_file.write_bytes(b"content")
        # Não deve lançar exceção
        conv.validate_input_file(test_file)


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


def test_ensure_paths_different_extensions(tmp_path: Path):
    # Teste com diferentes extensões
    extensions = [".pdf", ".docx", ".html", ".png"]
    
    for ext in extensions:
        test_file = tmp_path / f"file{ext}"
        test_file.write_bytes(b"content")
        outdir = tmp_path / "output"
        
        md, txt = conv.ensure_paths(test_file, outdir)
        assert md.name == "file.md"
        assert txt.name == "file.txt"
        assert outdir.exists()


def test_ensure_paths_spaces_in_filename(tmp_path: Path):
    # Teste com espaços no nome do arquivo
    test_file = tmp_path / "arquivo com espaços.pdf"
    test_file.write_bytes(b"%PDF-1.4\n")
    outdir = tmp_path / "output"
    
    md, txt = conv.ensure_paths(test_file, outdir)
    # Espaços devem ser substituídos por underline
    assert md.name == "arquivo_com_espaços.md"
    assert txt.name == "arquivo_com_espaços.txt"
    assert outdir.exists()


def test_ensure_paths_multiple_spaces_and_special_chars(tmp_path: Path):
    # Teste com múltiplos espaços e caracteres especiais
    test_file = tmp_path / "Súmulas  TCU   atualizado.docx"
    test_file.write_bytes(b"content")
    outdir = tmp_path / "output"
    
    md, txt = conv.ensure_paths(test_file, outdir)
    # Múltiplos espaços devem ser substituídos individualmente
    assert md.name == "Súmulas__TCU___atualizado.md"
    assert txt.name == "Súmulas__TCU___atualizado.txt"
    assert outdir.exists()


def test_convert_with_docling_success_pdf(tmp_path: Path, monkeypatch):
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


def test_convert_with_docling_success_docx(tmp_path: Path, monkeypatch):
    indocx = tmp_path / "test.docx"
    indocx.write_bytes(b"fake docx content")

    class FakeDoc:
        def export_to_markdown(self):
            return "# DOCX converted"

    class FakeRes:
        document = FakeDoc()

    class FakeConverter:
        def convert(self, s: str):
            assert s == str(indocx)
            return FakeRes()

    # Simular módulo docling.document_converter
    fake_mod = types.SimpleNamespace(DocumentConverter=FakeConverter)
    sys.modules["docling.document_converter"] = fake_mod

    md = conv.convert_with_docling(indocx)
    assert md.strip() == "# DOCX converted"


def test_convert_with_docling_alternative_export_methods(tmp_path: Path, monkeypatch):
    infile = tmp_path / "test.html"
    infile.write_text("<html><body>Test</body></html>")

    class FakeDoc:
        # Teste método alternativo export_to_markdown_str
        def export_to_markdown_str(self):
            return "# Alternative method"

    class FakeRes:
        document = FakeDoc()

    class FakeConverter:
        def convert(self, s: str):
            return FakeRes()

    fake_mod = types.SimpleNamespace(DocumentConverter=FakeConverter)
    sys.modules["docling.document_converter"] = fake_mod

    md = conv.convert_with_docling(infile)
    assert md.strip() == "# Alternative method"


def test_convert_with_docling_missing_api(tmp_path: Path):
    inpdf = tmp_path / "a.pdf"
    inpdf.write_bytes(b"%PDF-1.4\n")

    # Remover módulo para simular indisponibilidade
    sys.modules.pop("docling.document_converter", None)

    md = conv.convert_with_docling(inpdf)
    assert md is None


def test_convert_document_function_multiple_extensions(tmp_path: Path, monkeypatch):
    # Teste da função convert_document com diferentes extensões
    files_to_test = [
        ("test.pdf", b"%PDF-1.4\n"),
        ("test.docx", b"fake docx"),
        ("test.html", b"<html><body>Test</body></html>"),
        ("test.md", b"# Markdown test"),
    ]
    
    for filename, content in files_to_test:
        test_file = tmp_path / filename
        test_file.write_bytes(content)
        
        # Mock bem simples - falha no Docling, usa fallback
        sys.modules.pop("docling.document_converter", None)
        
        # Para PDF, usar PyMuPDF mock
        if filename.endswith('.pdf'):
            class FakePage:
                def get_text(self) -> str:
                    return "mocked text"
            class FakeDoc:
                def __len__(self) -> int:
                    return 1
                def load_page(self, i: int):
                    return FakePage()
                def close(self) -> None:
                    pass
            monkeypatch.setitem(sys.modules, "fitz", types.SimpleNamespace(open=lambda p: FakeDoc()))
        
        result = conv.convert_document(str(test_file), str(tmp_path / "output"))
        
        # Verificar que a conversão foi realizada
        assert result["success"] is True
        assert result["output_file"] is not None
        assert Path(result["output_file"]).exists()


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


def test_fallback_with_pymupdf_non_pdf(tmp_path: Path):
    # PyMuPDF fallback só deve funcionar com PDFs
    docx = tmp_path / "test.docx"
    docx.write_bytes(b"content")
    
    with pytest.raises(ValueError, match="PyMuPDF fallback só suporta PDF"):
        conv.fallback_with_pymupdf(docx)


def test_get_generic_fallback_text_file(tmp_path: Path):
    # Testar fallback genérico com arquivo de texto
    md_file = tmp_path / "test.md"
    content = "# Título\n\nConteúdo do markdown"
    md_file.write_text(content, encoding='utf-8')
    
    result = conv.get_generic_fallback(md_file)
    assert "test.md" in result
    assert content in result


def test_get_generic_fallback_html_file(tmp_path: Path):
    # Testar com arquivo HTML
    html_file = tmp_path / "test.html"
    content = "<html><body><h1>Test</h1></body></html>"
    html_file.write_text(content, encoding='utf-8')
    
    result = conv.get_generic_fallback(html_file)
    assert "test.html" in result
    assert content in result


def test_get_generic_fallback_unsupported_binary(tmp_path: Path):
    # Testar com arquivo binário não suportado
    bin_file = tmp_path / "test.exe"
    bin_file.write_bytes(b"\x00\x01\x02\x03")
    
    result = conv.get_generic_fallback(bin_file)
    assert "test.exe" in result
    assert "não pôde ser processado" in result
