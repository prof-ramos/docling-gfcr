from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
import pytest

# Garantir que o diretório do projeto esteja no sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import scripts.markdown_agent as agent


@pytest.fixture
def markdown_agent():
    """Fixture para instância do MarkdownAgent."""
    return agent.MarkdownAgent()


@pytest.fixture
def sample_pdf(tmp_path):
    """Fixture para arquivo PDF de teste."""
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n")
    return pdf_file


def test_analyze_document(markdown_agent, sample_pdf):
    """Testa análise de documento."""
    analysis = markdown_agent.analyze_document(sample_pdf)
    
    assert analysis["filename"] == "test.pdf"
    assert analysis["extension"] == ".pdf"
    assert analysis["is_supported"] is True
    assert analysis["size_bytes"] > 0
    assert "estimated_pages" in analysis


def test_analyze_unsupported_document(markdown_agent, tmp_path):
    """Testa análise de formato não suportado."""
    unsupported_file = tmp_path / "test.xyz"
    unsupported_file.write_text("conteúdo")
    
    analysis = markdown_agent.analyze_document(unsupported_file)
    
    assert analysis["extension"] == ".xyz"
    assert analysis["is_supported"] is False


def test_optimize_markdown(markdown_agent):
    """Testa otimização de conteúdo Markdown."""
    raw_content = """# Título


Parágrafo com muito espaço.



## Subtítulo
Lista:
- Item 1
- Item 2
Texto após lista."""
    
    optimized = markdown_agent.optimize_markdown(raw_content, "test.pdf")
    
    # Verifica metadados adicionados
    assert "---" in optimized
    assert "title: test" in optimized
    assert "converted_by: Docling Markdown Agent" in optimized
    
    # Verifica limpeza de espaços excessivos
    assert "\n\n\n" not in optimized
    
    # Verifica que termina com quebra de linha
    assert optimized.endswith('\n')


def test_validate_markdown_quality(markdown_agent):
    """Testa validação de qualidade do Markdown."""
    good_content = """# Título Principal

Este é um parágrafo bem formado.

## Seção

Outro parágrafo com conteúdo.

- Lista item 1
- Lista item 2

Mais conteúdo após a lista."""
    
    validation = markdown_agent.validate_markdown(good_content)
    
    assert validation["valid"] is True
    assert validation["quality_score"] >= 80
    assert validation["metrics"]["headers_count"] >= 2
    assert validation["metrics"]["word_count"] > 10


def test_validate_poor_markdown(markdown_agent):
    """Testa validação de Markdown de baixa qualidade."""
    poor_content = "Apenas texto sem estrutura"
    
    validation = markdown_agent.validate_markdown(poor_content)
    
    assert validation["valid"] is False
    assert len(validation["issues"]) > 0
    assert validation["quality_score"] < 100


def test_convert_document_success(markdown_agent, sample_pdf, tmp_path, monkeypatch):
    """Testa conversão bem-sucedida de documento."""
    output_dir = tmp_path / "output"
    
    # Mock da função convert_with_docling
    mock_content = "# Documento Convertido\n\nConteúdo do documento."
    monkeypatch.setattr("scripts.markdown_agent.convert_with_docling", lambda p: mock_content)
    
    result = markdown_agent.convert_document(
        input_path=str(sample_pdf),
        output_dir=str(output_dir),
        optimize=True,
        validate=True,
        return_content=True
    )
    
    assert result["success"] is True
    assert result["agent"] == "markdown_agent"
    assert result["conversion_method"] == "docling"
    assert result["optimized"] is True
    assert result["validated"] is True
    assert "validation" in result
    assert "content" in result
    assert "input_analysis" in result


def test_convert_document_fallback(markdown_agent, sample_pdf, tmp_path, monkeypatch):
    """Testa fallback para PyMuPDF."""
    output_dir = tmp_path / "output"
    
    # Mock: Docling falha, PyMuPDF funciona
    monkeypatch.setattr("scripts.markdown_agent.convert_with_docling", lambda p: None)
    monkeypatch.setattr("scripts.markdown_agent.fallback_with_pymupdf", lambda p: "Texto extraído")
    
    result = markdown_agent.convert_document(
        input_path=str(sample_pdf),
        output_dir=str(output_dir)
    )
    
    assert result["success"] is True
    assert result["conversion_method"] == "pymupdf_fallback"


def test_convert_unsupported_format(markdown_agent, tmp_path):
    """Testa conversão de formato não suportado."""
    unsupported_file = tmp_path / "test.xyz"
    unsupported_file.write_text("conteúdo")
    
    result = markdown_agent.convert_document(str(unsupported_file))
    
    assert result["success"] is False
    assert "não suportado" in result["error"]
    assert "supported_formats" in result


def test_convert_file_not_found(markdown_agent):
    """Testa conversão de arquivo inexistente."""
    result = markdown_agent.convert_document("/path/that/does/not/exist.pdf")
    
    assert result["success"] is False
    assert "não encontrado" in result["error"]


def test_batch_convert(markdown_agent, tmp_path, monkeypatch):
    """Testa conversão em lote."""
    # Criar arquivos de teste
    pdf1 = tmp_path / "doc1.pdf"
    pdf2 = tmp_path / "doc2.pdf"
    pdf1.write_bytes(b"%PDF-1.4\n")
    pdf2.write_bytes(b"%PDF-1.4\n")
    
    # Mock conversão
    monkeypatch.setattr("scripts.markdown_agent.convert_with_docling", lambda p: f"# {p.stem}")
    
    results = markdown_agent.batch_convert([str(pdf1), str(pdf2)])
    
    assert len(results) == 2
    assert all(r["success"] for r in results)
    assert results[0]["agent"] == "markdown_agent"
    assert results[1]["agent"] == "markdown_agent"


def test_main_single_conversion(tmp_path, monkeypatch):
    """Testa main() com conversão única."""
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n")
    
    # JSON de entrada
    input_data = {
        "input_path": str(pdf_file),
        "output_dir": str(tmp_path / "output"),
        "optimize": True,
        "validate": True,
        "return_content": True
    }
    
    # Mock stdin e stdout
    mock_stdin = mock_open(read_data=json.dumps(input_data))
    monkeypatch.setattr("sys.stdin", mock_stdin.return_value)
    
    captured_output = []
    def mock_print(*args, **kwargs):
        captured_output.append(args[0] if args else "")
    monkeypatch.setattr("builtins.print", mock_print)
    
    # Mock conversão
    monkeypatch.setattr("scripts.markdown_agent.convert_with_docling", lambda p: "# Teste")
    
    # Executar main
    agent.main()
    
    # Verificar saída
    output = captured_output[0]
    result = json.loads(output)
    
    assert result["success"] is True
    assert result["agent"] == "markdown_agent"
    assert "batch" not in result


def test_main_batch_conversion(tmp_path, monkeypatch):
    """Testa main() com conversão em lote."""
    pdf1 = tmp_path / "doc1.pdf"
    pdf2 = tmp_path / "doc2.pdf" 
    pdf1.write_bytes(b"%PDF-1.4\n")
    pdf2.write_bytes(b"%PDF-1.4\n")
    
    # JSON de entrada para lote
    input_data = {
        "input_path": [str(pdf1), str(pdf2)],
        "optimize": False
    }
    
    # Mock stdin
    mock_stdin = mock_open(read_data=json.dumps(input_data))
    monkeypatch.setattr("sys.stdin", mock_stdin.return_value)
    
    captured_output = []
    def mock_print(*args, **kwargs):
        captured_output.append(args[0] if args else "")
    monkeypatch.setattr("builtins.print", mock_print)
    
    # Mock conversão
    monkeypatch.setattr("scripts.markdown_agent.convert_with_docling", lambda p: f"# {p.stem}")
    
    # Executar main
    agent.main()
    
    # Verificar saída
    output = captured_output[0]
    result = json.loads(output)
    
    assert result["success"] is True
    assert result["batch"] is True
    assert len(result["results"]) == 2
    assert result["summary"]["total"] == 2


def test_main_missing_input_path(monkeypatch):
    """Testa main() sem input_path."""
    input_data = {"optimize": True}
    
    mock_stdin = mock_open(read_data=json.dumps(input_data))
    monkeypatch.setattr("sys.stdin", mock_stdin.return_value)
    
    captured_output = []
    def mock_print(*args, **kwargs):
        captured_output.append(args[0] if args else "")
    monkeypatch.setattr("builtins.print", mock_print)
    
    exit_codes = []
    def mock_exit(code):
        exit_codes.append(code)
    monkeypatch.setattr("sys.exit", mock_exit)
    
    # Executar main
    agent.main()
    
    # Verificar erro
    output = captured_output[0]
    result = json.loads(output)
    
    assert result["success"] is False
    assert "obrigatório" in result["error"]
    assert exit_codes[0] == 1