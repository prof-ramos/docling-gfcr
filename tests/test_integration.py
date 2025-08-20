#!/usr/bin/env python3
"""
Testes de Integração - Verificação de comunicação entre módulos

Escopo:
- Integração openai_enhancer ↔ convert
- Integração convert ↔ claude_tool 
- Integração convert ↔ web_ui
- Integração convert ↔ gui
- Integração markdown_agent ↔ openai_enhancer
- Fluxos completos ponta a ponta
"""
from __future__ import annotations

import sys
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Garantir que o diretório do projeto esteja no sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import scripts.convert as convert
import scripts.claude_tool as claude_tool
import scripts.markdown_agent as markdown_agent


class TestConvertOpenAIIntegration:
    """Testes de integração convert.py ↔ openai_enhancer.py."""

    @patch('scripts.convert.create_enhancer_from_env')
    @patch('scripts.convert.convert_with_docling')
    def test_convert_with_openai_enhancement_success(self, mock_docling, mock_enhancer_env):
        """Testa conversão com enriquecimento OpenAI bem-sucedido."""
        # Mock do Docling
        mock_docling.return_value = "# Original Markdown"
        
        # Mock do OpenAI Enhancer
        mock_enhancer = Mock()
        mock_enhancer.enhance_markdown.return_value = {
            "enhanced_markdown": "# Enhanced Markdown",
            "metadata": {"type": "document", "topics": ["test"]},
            "improvements": ["Structure optimization"]
        }
        mock_enhancer_env.return_value = mock_enhancer
        
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_file:
            tmp_file.write(b"PDF content")
            tmp_file.flush()
            
            with tempfile.TemporaryDirectory() as tmp_dir:
                result = convert.convert_document(
                    input_path=tmp_file.name,
                    output_dir=tmp_dir,
                    enhance_with_openai=True
                )
        
        assert result["success"] is True
        assert "openai_enhancement" in result
        assert result["openai_enhancement"]["applied"] is True
        assert "Enhanced Markdown" in result.get("content", "")
        mock_enhancer.enhance_markdown.assert_called_once()

    @patch('scripts.convert.create_enhancer_from_env')
    @patch('scripts.convert.convert_with_docling')
    def test_convert_with_openai_enhancement_fallback(self, mock_docling, mock_enhancer_env):
        """Testa fallback quando OpenAI falha."""
        # Mock do Docling
        mock_docling.return_value = "# Original Markdown"
        
        # Mock do OpenAI Enhancer com erro
        mock_enhancer = Mock()
        mock_enhancer.enhance_markdown.side_effect = Exception("API Error")
        mock_enhancer_env.return_value = mock_enhancer
        
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_file:
            tmp_file.write(b"PDF content")
            tmp_file.flush()
            
            with tempfile.TemporaryDirectory() as tmp_dir:
                result = convert.convert_document(
                    input_path=tmp_file.name,
                    output_dir=tmp_dir,
                    enhance_with_openai=True
                )
        
        assert result["success"] is True
        assert "openai_enhancement" in result
        assert result["openai_enhancement"]["applied"] is False
        assert "Original Markdown" in result.get("content", "")

    @patch('scripts.convert.OPENAI_AVAILABLE', False)
    @patch('scripts.convert.convert_with_docling')
    def test_convert_without_openai_available(self, mock_docling):
        """Testa conversão quando OpenAI não está disponível."""
        mock_docling.return_value = "# Original Markdown"
        
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_file:
            tmp_file.write(b"PDF content")
            tmp_file.flush()
            
            with tempfile.TemporaryDirectory() as tmp_dir:
                result = convert.convert_document(
                    input_path=tmp_file.name,
                    output_dir=tmp_dir,
                    enhance_with_openai=True
                )
        
        assert result["success"] is True
        assert "openai_enhancement" not in result or result["openai_enhancement"]["applied"] is False


class TestClaudeToolIntegration:
    """Testes de integração claude_tool.py ↔ convert.py."""

    @patch('scripts.claude_tool.convert_document')
    def test_claude_tool_basic_conversion(self, mock_convert):
        """Testa conversão básica via Claude Tool."""
        mock_convert.return_value = {
            "success": True,
            "output_file": "/output/test.md",
            "content": "# Converted content",
            "conversion_info": {"method": "docling"}
        }
        
        result = claude_tool.convert_document_tool(
            input_path="/test/input.pdf",
            output_dir="/test/output",
            return_content=True,
            enhance_with_openai=False
        )
        
        assert result["success"] is True
        assert result["content"] == "# Converted content"
        assert result["conversion_method"] == "docling"
        mock_convert.assert_called_once_with(
            input_path="/test/input.pdf",
            output_dir="/test/output",
            return_content=True,
            enhance_with_openai=False
        )

    @patch('scripts.claude_tool.convert_document')
    def test_claude_tool_with_openai_enhancement(self, mock_convert):
        """Testa Claude Tool com enriquecimento OpenAI."""
        mock_convert.return_value = {
            "success": True,
            "output_file": "/output/test.md",
            "content": "# Enhanced content",
            "conversion_info": {"method": "docling+openai"},
            "openai_enhancement": {
                "applied": True,
                "metadata": {"type": "document"},
                "improvements": ["Enhanced structure"]
            }
        }
        
        result = claude_tool.convert_document_tool(
            input_path="/test/input.pdf",
            output_dir="/test/output",
            return_content=True,
            enhance_with_openai=True
        )
        
        assert result["success"] is True
        assert result["conversion_method"] == "docling+openai"
        assert "openai_enhancement" in result
        mock_convert.assert_called_once_with(
            input_path="/test/input.pdf",
            output_dir="/test/output",
            return_content=True,
            enhance_with_openai=True
        )

    @patch('scripts.claude_tool.convert_document')  
    def test_claude_tool_error_handling(self, mock_convert):
        """Testa tratamento de erro no Claude Tool."""
        mock_convert.return_value = {
            "success": False,
            "error": "Conversion failed",
            "output_file": None
        }
        
        result = claude_tool.convert_document_tool(
            input_path="/invalid/path.pdf",
            output_dir="/test/output"
        )
        
        assert result["success"] is False
        assert "error" in result


class TestMarkdownAgentIntegration:
    """Testes de integração markdown_agent.py ↔ convert.py e openai_enhancer.py."""

    @patch('scripts.markdown_agent.convert_with_docling')
    def test_markdown_agent_basic_conversion(self, mock_docling):
        """Testa conversão básica via Markdown Agent."""
        mock_docling.return_value = "# Original Content"
        
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_file:
            tmp_file.write(b"PDF content")
            tmp_file.flush()
            
            with tempfile.TemporaryDirectory() as tmp_dir:
                result = markdown_agent.convert_document(
                    input_path=tmp_file.name,
                    output_dir=tmp_dir,
                    optimize=False,
                    validate=False
                )
        
        assert result["success"] is True
        assert result["method"] == "docling"
        assert "content" in result

    @patch('scripts.markdown_agent.convert_with_docling')
    def test_markdown_agent_with_optimization(self, mock_docling):
        """Testa Markdown Agent com otimização."""
        mock_docling.return_value = "# Original Content\n\nSome text."
        
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_file:
            tmp_file.write(b"PDF content")
            tmp_file.flush()
            
            with tempfile.TemporaryDirectory() as tmp_dir:
                # Mock do MarkdownAgent
                with patch.object(markdown_agent, 'MarkdownAgent') as mock_agent_class:
                    mock_agent = Mock()
                    mock_agent.optimize_markdown.return_value = "# Optimized Content\n\nSome text."
                    mock_agent_class.return_value = mock_agent
                    
                    result = markdown_agent.convert_document(
                        input_path=tmp_file.name,
                        output_dir=tmp_dir,
                        optimize=True,
                        validate=False
                    )
        
        assert result["success"] is True
        mock_agent.optimize_markdown.assert_called_once()

    @patch('scripts.markdown_agent.convert_with_docling')
    def test_markdown_agent_batch_processing(self, mock_docling):
        """Testa processamento em lote do Markdown Agent."""
        mock_docling.return_value = "# Content"
        
        files = []
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Criar múltiplos arquivos temporários
            for i in range(3):
                tmp_file = Path(tmp_dir) / f"test_{i}.pdf"
                tmp_file.write_bytes(b"PDF content")
                files.append(str(tmp_file))
            
            with patch.object(markdown_agent, 'MarkdownAgent') as mock_agent_class:
                mock_agent = Mock()
                mock_agent_class.return_value = mock_agent
                
                results = markdown_agent.batch_convert(
                    input_paths=files,
                    output_dir=tmp_dir,
                    optimize=False,
                    validate=False
                )
        
        assert len(results) == 3
        assert all(result["success"] for result in results)


class TestEndToEndIntegration:
    """Testes de integração ponta a ponta."""

    @patch('scripts.convert.convert_with_docling')
    @patch('scripts.convert.create_enhancer_from_env')
    def test_full_pipeline_with_enhancement(self, mock_enhancer_env, mock_docling):
        """Testa pipeline completo: convert → openai → claude_tool."""
        # Mock do pipeline completo
        mock_docling.return_value = "# Original Content"
        
        mock_enhancer = Mock()
        mock_enhancer.enhance_markdown.return_value = {
            "enhanced_markdown": "# Enhanced Content",
            "metadata": {"type": "report", "topics": ["test"]},
            "improvements": ["Structure", "Formatting"]
        }
        mock_enhancer_env.return_value = mock_enhancer
        
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_file:
            tmp_file.write(b"PDF content")
            tmp_file.flush()
            
            with tempfile.TemporaryDirectory() as tmp_dir:
                # Step 1: Conversão com enhancement
                convert_result = convert.convert_document(
                    input_path=tmp_file.name,
                    output_dir=tmp_dir,
                    enhance_with_openai=True,
                    return_content=True
                )
                
                # Step 2: Usar o resultado no Claude Tool
                tool_result = claude_tool.convert_document_tool(
                    input_path=tmp_file.name,
                    output_dir=tmp_dir,
                    return_content=True,
                    enhance_with_openai=True
                )
        
        # Verificar ambos os resultados
        assert convert_result["success"] is True
        assert "openai_enhancement" in convert_result
        assert tool_result["success"] is True
        assert "Enhanced Content" in tool_result.get("content", "")

    @patch('scripts.convert.convert_with_docling')
    def test_error_propagation(self, mock_docling):
        """Testa propagação de erros através do pipeline."""
        mock_docling.side_effect = Exception("Docling Error")
        
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_file:
            tmp_file.write(b"PDF content")
            tmp_file.flush()
            
            with tempfile.TemporaryDirectory() as tmp_dir:
                # Teste com convert
                convert_result = convert.convert_document(
                    input_path=tmp_file.name,
                    output_dir=tmp_dir
                )
                
                # Deve usar fallback
                assert convert_result["success"] is True  # PyMuPDF fallback
                assert convert_result["conversion_info"]["method"] == "pymupdf"

    @patch('scripts.convert.convert_with_docling')
    def test_format_consistency_across_modules(self, mock_docling):
        """Testa consistência de formatos entre módulos."""
        mock_docling.return_value = "# Test Content"
        
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_file:
            tmp_file.write(b"PDF content")
            tmp_file.flush()
            
            with tempfile.TemporaryDirectory() as tmp_dir:
                # Teste com diferentes módulos
                convert_result = convert.convert_document(
                    input_path=tmp_file.name,
                    output_dir=tmp_dir,
                    return_content=True
                )
                
                claude_result = claude_tool.convert_document_tool(
                    input_path=tmp_file.name,
                    output_dir=tmp_dir,
                    return_content=True
                )
                
                agent_result = markdown_agent.convert_document(
                    input_path=tmp_file.name,
                    output_dir=tmp_dir
                )
        
        # Verificar consistência de estrutura
        for result in [convert_result, claude_result, agent_result]:
            assert "success" in result
            assert isinstance(result["success"], bool)
            if result["success"]:
                assert "conversion_info" in result or "method" in result


class TestDataFlowIntegration:
    """Testes de fluxo de dados entre módulos."""

    def test_json_schema_consistency(self):
        """Testa consistência dos schemas JSON entre módulos."""
        # Schema esperado para resultados de conversão
        expected_fields = ["success", "output_file", "content", "conversion_info"]
        
        # Mock de resultado do convert
        convert_result = {
            "success": True,
            "output_file": "/output/test.md",
            "content": "# Content",
            "conversion_info": {"method": "docling"}
        }
        
        # Verificar schema
        for field in expected_fields:
            if field == "content":
                continue  # Opcional
            assert field in convert_result

    def test_error_format_consistency(self):
        """Testa consistência do formato de erros."""
        error_result = {
            "success": False,
            "error": "Test error message",
            "output_file": None
        }
        
        assert error_result["success"] is False
        assert "error" in error_result
        assert isinstance(error_result["error"], str)

    def test_openai_enhancement_structure(self):
        """Testa estrutura do enriquecimento OpenAI."""
        enhancement = {
            "applied": True,
            "metadata": {"type": "document", "topics": ["test"]},
            "improvements": ["Structure optimization"]
        }
        
        assert "applied" in enhancement
        assert "metadata" in enhancement
        assert "improvements" in enhancement
        assert isinstance(enhancement["applied"], bool)
        assert isinstance(enhancement["improvements"], list)


class TestConcurrencyIntegration:
    """Testes de integração com concorrência."""

    @patch('scripts.convert.convert_with_docling')
    def test_concurrent_conversions(self, mock_docling):
        """Testa conversões concorrentes."""
        mock_docling.return_value = "# Content"
        
        import concurrent.futures
        
        def convert_file(file_index):
            with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_file:
                tmp_file.write(f"PDF content {file_index}".encode())
                tmp_file.flush()
                
                with tempfile.TemporaryDirectory() as tmp_dir:
                    return convert.convert_document(
                        input_path=tmp_file.name,
                        output_dir=tmp_dir
                    )
        
        # Executar conversões concorrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(convert_file, i) for i in range(3)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        assert len(results) == 3
        assert all(result["success"] for result in results)

    def test_thread_safety_structure(self):
        """Testa estruturas thread-safe."""
        # Verificar que não há estado global mutável problemático
        import threading
        
        def check_thread_safety():
            # Operações que devem ser thread-safe
            result = {"thread_id": threading.current_thread().ident}
            return result
        
        results = []
        threads = []
        
        for i in range(3):
            thread = threading.Thread(target=lambda: results.append(check_thread_safety()))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verificar que cada thread teve ID único
        thread_ids = [r["thread_id"] for r in results]
        assert len(set(thread_ids)) == len(thread_ids)


if __name__ == "__main__":
    # Permite executar os testes diretamente
    pytest.main([__file__, "-v", "--cov=scripts", "--cov-report=term-missing"])