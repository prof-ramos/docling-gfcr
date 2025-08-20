from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from unittest.mock import patch, mock_open
import pytest

# Garantir que o diretório do projeto esteja no sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import scripts.claude_tool as tool


def test_tool_schema_structure():
    """Testa se o schema do tool está bem formado."""
    schema = tool.TOOL_SCHEMA
    
    assert schema["name"] == "convert_document"
    assert "description" in schema
    assert "input_schema" in schema
    
    # Verifica propriedades do input_schema
    properties = schema["input_schema"]["properties"]
    assert "input_path" in properties
    assert "output_dir" in properties
    assert "return_content" in properties
    
    # Verifica que input_path é obrigatório
    assert "input_path" in schema["input_schema"]["required"]


def test_convert_document_tool_success(tmp_path, monkeypatch):
    """Testa conversão bem-sucedida com Docling."""
    # Criar arquivo PDF de teste
    input_pdf = tmp_path / "test.pdf"
    input_pdf.write_bytes(b"%PDF-1.4\n")
    
    output_dir = tmp_path / "output"
    
    # Mock da função convert_with_docling
    monkeypatch.setattr(tool, "convert_with_docling", lambda p: "# Markdown content")
    monkeypatch.setattr(tool, "fallback_with_pymupdf", lambda p: "Text content")
    
    result = tool.convert_document_tool(
        input_path=str(input_pdf),
        output_dir=str(output_dir),
        return_content=True
    )
    
    assert result["success"] is True
    assert result["conversion_method"] == "docling"
    assert result["output_file"].endswith("test.md")
    assert result["content"] == "# Markdown content"
    assert result["file_size_bytes"] > 0


def test_convert_document_tool_fallback(tmp_path, monkeypatch):
    """Testa fallback para PyMuPDF quando Docling falha."""
    input_pdf = tmp_path / "test.pdf"
    input_pdf.write_bytes(b"%PDF-1.4\n")
    
    output_dir = tmp_path / "output"
    
    # Mock: Docling retorna None, força fallback
    monkeypatch.setattr(tool, "convert_with_docling", lambda p: None)
    monkeypatch.setattr(tool, "fallback_with_pymupdf", lambda p: "Extracted text")
    
    result = tool.convert_document_tool(
        input_path=str(input_pdf),
        output_dir=str(output_dir),
        return_content=True
    )
    
    assert result["success"] is True
    assert result["conversion_method"] == "pymupdf_fallback"
    assert result["output_file"].endswith("test.txt")
    assert result["content"] == "Extracted text"


def test_convert_document_tool_file_not_found():
    """Testa tratamento de arquivo não encontrado."""
    result = tool.convert_document_tool(
        input_path="/path/that/does/not/exist.pdf",
        output_dir="/tmp/output"
    )
    
    assert result["success"] is False
    assert "não encontrado" in result["error"]


def test_convert_document_tool_without_content_return(tmp_path, monkeypatch):
    """Testa conversão sem retornar conteúdo na resposta."""
    input_pdf = tmp_path / "test.pdf"
    input_pdf.write_bytes(b"%PDF-1.4\n")
    
    output_dir = tmp_path / "output"
    
    monkeypatch.setattr(tool, "convert_with_docling", lambda p: "# Markdown")
    
    result = tool.convert_document_tool(
        input_path=str(input_pdf),
        output_dir=str(output_dir),
        return_content=False  # Não retornar conteúdo
    )
    
    assert result["success"] is True
    assert "content" not in result  # Conteúdo não deve estar na resposta
    assert result["output_file"].endswith("test.md")


def test_main_with_valid_json_input(tmp_path, monkeypatch):
    """Testa main() com entrada JSON válida."""
    input_pdf = tmp_path / "test.pdf"
    input_pdf.write_bytes(b"%PDF-1.4\n")
    
    # Mock stdin com JSON válido
    json_input = {
        "input_path": str(input_pdf),
        "output_dir": str(tmp_path / "output"),
        "return_content": True
    }
    
    mock_stdin = mock_open(read_data=json.dumps(json_input))
    monkeypatch.setattr("sys.stdin", mock_stdin.return_value)
    
    # Mock funções de conversão
    monkeypatch.setattr(tool, "convert_with_docling", lambda p: "# Test")
    
    # Capturar stdout
    captured_output = []
    def mock_print(content):
        captured_output.append(content)
    monkeypatch.setattr("builtins.print", mock_print)
    
    # Executar main
    tool.main()
    
    # Verificar saída JSON
    output = captured_output[0]
    result = json.loads(output)
    
    assert result["success"] is True
    assert result["conversion_method"] == "docling"


def test_main_with_invalid_json_input(monkeypatch):
    """Testa main() com entrada JSON inválida."""
    # Mock stdin com JSON inválido
    mock_stdin = mock_open(read_data="invalid json")
    monkeypatch.setattr("sys.stdin", mock_stdin.return_value)
    
    # Capturar stdout
    captured_output = []
    def mock_print(content):
        captured_output.append(content)
    monkeypatch.setattr("builtins.print", mock_print)
    
    # Mock sys.exit para capturar código de saída
    exit_code = []
    def mock_exit(code):
        exit_code.append(code)
    monkeypatch.setattr("sys.exit", mock_exit)
    
    # Executar main
    tool.main()
    
    # Verificar erro JSON e código de saída
    output = captured_output[0]
    result = json.loads(output)
    
    assert result["success"] is False
    assert "Erro ao decodificar JSON" in result["error"]
    assert exit_code[0] == 1


def test_main_missing_required_parameter(monkeypatch):
    """Testa main() sem parâmetro obrigatório."""
    # JSON sem input_path
    json_input = {
        "output_dir": "/tmp/output"
    }
    
    mock_stdin = mock_open(read_data=json.dumps(json_input))
    monkeypatch.setattr("sys.stdin", mock_stdin.return_value)
    
    captured_output = []
    def mock_print(content):
        captured_output.append(content)
    monkeypatch.setattr("builtins.print", mock_print)
    
    tool.main()
    
    output = captured_output[0]
    result = json.loads(output)
    
    assert result["success"] is False
    assert "obrigatório" in result["error"]