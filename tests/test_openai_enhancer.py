#!/usr/bin/env python3
"""
Testes abrangentes para o módulo openai_enhancer.py

Cobertura de testes:
- Classe OpenAIEnhancer (inicialização, métodos principais)
- Funções auxiliares
- Tratamento de erros e edge cases
- Mocking da API OpenAI
"""
from __future__ import annotations

import json
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Garantir que o diretório do projeto esteja no sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import scripts.openai_enhancer as enhancer


class TestOpenAIEnhancer:
    """Testes para a classe OpenAIEnhancer."""

    @patch('scripts.openai_enhancer.OpenAI')
    def test_init_with_api_key(self, mock_openai):
        """Testa inicialização com API key explícita."""
        api_key = "test-api-key"
        model = "gpt-4o-mini"
        
        client = enhancer.OpenAIEnhancer(api_key=api_key, model=model)
        
        assert client.model == model
        assert client.temperature == enhancer.DEFAULT_TEMPERATURE
        assert client.max_tokens == enhancer.DEFAULT_MAX_TOKENS
        mock_openai.assert_called_once_with(api_key=api_key)

    @patch('scripts.openai_enhancer.OpenAI')
    def test_init_with_environment_key(self, mock_openai):
        """Testa inicialização usando OPENAI_API_KEY do ambiente."""
        client = enhancer.OpenAIEnhancer()
        
        assert client.model == enhancer.DEFAULT_MODEL
        mock_openai.assert_called_once_with()

    @patch('scripts.openai_enhancer.OpenAI')
    def test_init_with_custom_parameters(self, mock_openai):
        """Testa inicialização com parâmetros customizados."""
        custom_temp = 0.7
        custom_tokens = 1500
        custom_model = "gpt-3.5-turbo"
        
        client = enhancer.OpenAIEnhancer(
            temperature=custom_temp,
            max_tokens=custom_tokens,
            model=custom_model
        )
        
        assert client.temperature == custom_temp
        assert client.max_tokens == custom_tokens
        assert client.model == custom_model

    @patch('scripts.openai_enhancer.OpenAI')
    def test_make_request_success(self, mock_openai):
        """Testa requisição bem-sucedida para API OpenAI."""
        # Setup mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"enhanced_markdown": "# Test", "metadata": {}}'
        mock_response.usage.total_tokens = 150
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        client = enhancer.OpenAIEnhancer(api_key="test-key")
        result = client._make_request("test prompt", "system prompt")
        
        assert "enhanced_markdown" in result
        assert result["enhanced_markdown"] == "# Test"
        mock_client.chat.completions.create.assert_called_once()

    @patch('scripts.openai_enhancer.OpenAI')
    def test_make_request_json_error(self, mock_openai):
        """Testa tratamento de erro JSON inválido."""
        # Setup mock response with invalid JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = 'invalid json'
        mock_response.usage.total_tokens = 100
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        client = enhancer.OpenAIEnhancer(api_key="test-key")
        result = client._make_request("test prompt")
        
        assert "error" in result
        assert "Erro de decodificação JSON" in result["error"]

    @patch('scripts.openai_enhancer.OpenAI')
    def test_make_request_api_error(self, mock_openai):
        """Testa tratamento de erro da API OpenAI."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        client = enhancer.OpenAIEnhancer(api_key="test-key")
        result = client._make_request("test prompt")
        
        assert "error" in result
        assert "API Error" in result["error"]

    @patch.object(enhancer.OpenAIEnhancer, '_make_request')
    @patch('scripts.openai_enhancer.OpenAI')
    def test_enhance_markdown_success(self, mock_openai, mock_request):
        """Testa enriquecimento bem-sucedido de Markdown."""
        mock_request.return_value = {
            "enhanced_markdown": "# Enhanced Content",
            "metadata": {"type": "document", "main_topics": ["test"]},
            "improvements": ["Header formatting", "Structure optimization"]
        }
        
        client = enhancer.OpenAIEnhancer(api_key="test-key")
        result = client.enhance_markdown("# Original Content")
        
        assert result["enhanced_markdown"] == "# Enhanced Content"
        assert "metadata" in result
        assert "improvements" in result
        mock_request.assert_called_once()

    @patch.object(enhancer.OpenAIEnhancer, '_make_request')
    @patch('scripts.openai_enhancer.OpenAI')
    def test_enhance_markdown_error(self, mock_openai, mock_request):
        """Testa tratamento de erro no enriquecimento."""
        original_content = "# Original Content"
        mock_request.return_value = {"error": "API Error"}
        
        client = enhancer.OpenAIEnhancer(api_key="test-key")
        result = client.enhance_markdown(original_content)
        
        # Deve retornar conteúdo original como fallback
        assert result["enhanced_markdown"] == original_content
        assert "error" in result
        assert result["metadata"]["type"] == "unknown"

    @patch.object(enhancer.OpenAIEnhancer, '_make_request')
    @patch('scripts.openai_enhancer.OpenAI')
    def test_analyze_document(self, mock_openai, mock_request):
        """Testa análise de documento."""
        mock_request.return_value = {
            "summary": "Test document summary",
            "key_points": ["Point 1", "Point 2"],
            "document_type": "technical_report",
            "topics": ["technology", "analysis"],
            "confidence": 0.95
        }
        
        client = enhancer.OpenAIEnhancer(api_key="test-key")
        result = client.analyze_document("Document content")
        
        assert result["summary"] == "Test document summary"
        assert len(result["key_points"]) == 2
        assert result["document_type"] == "technical_report"
        assert result["confidence"] == 0.95

    @patch.object(enhancer.OpenAIEnhancer, '_make_request')
    @patch('scripts.openai_enhancer.OpenAI')
    def test_extract_key_information(self, mock_openai, mock_request):
        """Testa extração de informações-chave."""
        mock_request.return_value = {
            "facts": ["Fact 1", "Fact 2"],
            "numbers": {"revenue": 1000000, "growth": 15.5},
            "dates": ["2023-01-01", "2023-12-31"],
            "entities": {"companies": ["Company A"], "people": ["John Doe"]}
        }
        
        client = enhancer.OpenAIEnhancer(api_key="test-key")
        result = client.extract_key_information("Document with facts")
        
        assert "facts" in result
        assert "numbers" in result
        assert "dates" in result
        assert "entities" in result

    @patch.object(enhancer.OpenAIEnhancer, 'enhance_markdown')
    @patch('scripts.openai_enhancer.OpenAI')
    def test_batch_enhance_documents_success(self, mock_openai, mock_enhance):
        """Testa processamento em lote bem-sucedido."""
        mock_enhance.return_value = {
            "enhanced_markdown": "# Enhanced",
            "metadata": {},
            "improvements": []
        }
        
        documents = [
            {"path": "/doc1.md", "content": "# Doc 1"},
            {"path": "/doc2.md", "content": "# Doc 2"}
        ]
        
        client = enhancer.OpenAIEnhancer(api_key="test-key")
        results = client.batch_enhance_documents(documents, "enhance")
        
        assert len(results) == 2
        assert all("source_path" in result for result in results)
        assert mock_enhance.call_count == 2

    @patch.object(enhancer.OpenAIEnhancer, 'analyze_document')
    @patch('scripts.openai_enhancer.OpenAI')
    def test_batch_enhance_documents_analyze(self, mock_openai, mock_analyze):
        """Testa processamento em lote para análise."""
        mock_analyze.return_value = {"summary": "Test analysis"}
        
        documents = [{"path": "/doc.md", "content": "Content"}]
        
        client = enhancer.OpenAIEnhancer(api_key="test-key")
        results = client.batch_enhance_documents(documents, "analyze")
        
        assert len(results) == 1
        assert results[0]["summary"] == "Test analysis"
        mock_analyze.assert_called_once()

    @patch.object(enhancer.OpenAIEnhancer, 'extract_key_information')
    @patch('scripts.openai_enhancer.OpenAI')
    def test_batch_enhance_documents_extract(self, mock_openai, mock_extract):
        """Testa processamento em lote para extração."""
        mock_extract.return_value = {"facts": ["Fact"]}
        
        documents = [{"path": "/doc.md", "content": "Content"}]
        
        client = enhancer.OpenAIEnhancer(api_key="test-key")
        results = client.batch_enhance_documents(documents, "extract")
        
        assert len(results) == 1
        assert results[0]["facts"] == ["Fact"]
        mock_extract.assert_called_once()

    @patch('scripts.openai_enhancer.OpenAI')
    def test_batch_enhance_invalid_operation(self, mock_openai):
        """Testa operação inválida no processamento em lote."""
        documents = [{"path": "/doc.md", "content": "Content"}]
        
        client = enhancer.OpenAIEnhancer(api_key="test-key")
        results = client.batch_enhance_documents(documents, "invalid_op")
        
        assert len(results) == 1
        assert "error" in results[0]
        assert "Operação inválida" in results[0]["error"]

    @patch('scripts.openai_enhancer.OpenAI')
    def test_batch_enhance_documents_error_handling(self, mock_openai):
        """Testa tratamento de erro no processamento em lote."""
        documents = [{"path": "/doc.md", "content": "Content"}]
        
        client = enhancer.OpenAIEnhancer(api_key="test-key")
        
        # Simular erro no método enhance_markdown
        with patch.object(client, 'enhance_markdown', side_effect=Exception("Process error")):
            results = client.batch_enhance_documents(documents, "enhance")
            
            assert len(results) == 1
            assert "error" in results[0]
            assert "Process error" in results[0]["error"]


class TestUtilityFunctions:
    """Testes para funções auxiliares."""

    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODEL': 'gpt-3.5-turbo',
        'OPENAI_TEMPERATURE': '0.5',
        'OPENAI_MAX_TOKENS': '1500'
    })
    @patch('scripts.openai_enhancer.OpenAI')
    def test_create_enhancer_from_env_success(self, mock_openai):
        """Testa criação do enhancer usando variáveis de ambiente."""
        client = enhancer.create_enhancer_from_env()
        
        assert client.model == 'gpt-3.5-turbo'
        assert client.temperature == 0.5
        assert client.max_tokens == 1500

    @patch.dict(os.environ, {}, clear=True)
    def test_create_enhancer_from_env_missing_key(self):
        """Testa erro quando OPENAI_API_KEY não está definida."""
        with pytest.raises(ValueError, match="OPENAI_API_KEY não encontrada"):
            enhancer.create_enhancer_from_env()

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    @patch('scripts.openai_enhancer.OpenAI')
    def test_create_enhancer_from_env_defaults(self, mock_openai):
        """Testa criação com valores padrão."""
        client = enhancer.create_enhancer_from_env()
        
        assert client.model == enhancer.DEFAULT_MODEL
        assert client.temperature == enhancer.DEFAULT_TEMPERATURE
        assert client.max_tokens == enhancer.DEFAULT_MAX_TOKENS

    @patch('scripts.openai_enhancer.OpenAIEnhancer')
    def test_enhance_markdown_content_with_key(self, mock_enhancer_class):
        """Testa função utilitária com API key."""
        mock_instance = Mock()
        mock_instance.enhance_markdown.return_value = {"enhanced_markdown": "# Enhanced"}
        mock_enhancer_class.return_value = mock_instance
        
        result = enhancer.enhance_markdown_content("# Content", "test-key")
        
        assert result["enhanced_markdown"] == "# Enhanced"
        mock_enhancer_class.assert_called_once_with(api_key="test-key")

    @patch('scripts.openai_enhancer.OpenAIEnhancer')
    def test_enhance_markdown_content_without_key(self, mock_enhancer_class):
        """Testa função utilitária sem API key."""
        mock_instance = Mock()
        mock_instance.enhance_markdown.return_value = {"enhanced_markdown": "# Enhanced"}
        mock_enhancer_class.return_value = mock_instance
        
        result = enhancer.enhance_markdown_content("# Content")
        
        assert result["enhanced_markdown"] == "# Enhanced"
        mock_enhancer_class.assert_called_once_with(api_key=None)


class TestPromptConstants:
    """Testes para validação dos prompts."""

    def test_markdown_enhancement_prompt_structure(self):
        """Testa estrutura do prompt de enriquecimento."""
        prompt = enhancer.MARKDOWN_ENHANCEMENT_PROMPT
        
        assert "Estruturação" in prompt
        assert "Formatação" in prompt
        assert "Clareza" in prompt
        assert "Metadados" in prompt
        assert "{content}" in prompt

    def test_document_analysis_prompt_structure(self):
        """Testa estrutura do prompt de análise."""
        prompt = enhancer.DOCUMENT_ANALYSIS_PROMPT
        
        assert "summary" in prompt
        assert "key_points" in prompt
        assert "document_type" in prompt
        assert "confidence" in prompt
        assert "{content}" in prompt

    def test_content_extraction_prompt_structure(self):
        """Testa estrutura do prompt de extração."""
        prompt = enhancer.CONTENT_EXTRACTION_PROMPT
        
        assert "informações mais importantes" in prompt
        assert "Dados factuais" in prompt
        assert "Números e estatísticas" in prompt
        assert "{content}" in prompt


class TestConstants:
    """Testes para constantes e configurações."""

    def test_default_constants(self):
        """Testa valores das constantes padrão."""
        assert enhancer.DEFAULT_MODEL == "gpt-4o-mini"
        assert enhancer.DEFAULT_TEMPERATURE == 0.3
        assert enhancer.DEFAULT_MAX_TOKENS == 2000

    def test_prompt_constants_exist(self):
        """Testa existência dos prompts principais."""
        assert hasattr(enhancer, 'MARKDOWN_ENHANCEMENT_PROMPT')
        assert hasattr(enhancer, 'DOCUMENT_ANALYSIS_PROMPT')
        assert hasattr(enhancer, 'CONTENT_EXTRACTION_PROMPT')

    def test_prompt_constants_non_empty(self):
        """Testa que os prompts não estão vazios."""
        assert len(enhancer.MARKDOWN_ENHANCEMENT_PROMPT.strip()) > 0
        assert len(enhancer.DOCUMENT_ANALYSIS_PROMPT.strip()) > 0
        assert len(enhancer.CONTENT_EXTRACTION_PROMPT.strip()) > 0


# Testes de edge cases e robustez
class TestEdgeCases:
    """Testes para casos extremos e robustez."""

    @patch('scripts.openai_enhancer.OpenAI')
    def test_empty_content_handling(self, mock_openai):
        """Testa tratamento de conteúdo vazio."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        client = enhancer.OpenAIEnhancer(api_key="test-key")
        
        with patch.object(client, '_make_request', return_value={"enhanced_markdown": ""}):
            result = client.enhance_markdown("")
            assert "enhanced_markdown" in result

    @patch('scripts.openai_enhancer.OpenAI')
    def test_very_large_content(self, mock_openai):
        """Testa tratamento de conteúdo muito grande."""
        large_content = "# Content\n" * 1000  # Conteúdo muito grande
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        client = enhancer.OpenAIEnhancer(api_key="test-key")
        
        with patch.object(client, '_make_request', return_value={"enhanced_markdown": "# Processed"}):
            result = client.enhance_markdown(large_content)
            assert result["enhanced_markdown"] == "# Processed"

    @patch('scripts.openai_enhancer.OpenAI')
    def test_unicode_content_handling(self, mock_openai):
        """Testa tratamento de conteúdo Unicode."""
        unicode_content = "# Título com acentos: ção, ã, ñ, 中文, 🚀"
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        client = enhancer.OpenAIEnhancer(api_key="test-key")
        
        with patch.object(client, '_make_request', return_value={"enhanced_markdown": unicode_content}):
            result = client.enhance_markdown(unicode_content)
            assert unicode_content in result["enhanced_markdown"]


if __name__ == "__main__":
    # Permite executar os testes diretamente
    pytest.main([__file__, "-v", "--cov=scripts.openai_enhancer", "--cov-report=term-missing"])