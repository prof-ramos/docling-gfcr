#!/usr/bin/env python3
"""
Módulo de integração OpenAI para melhorar conversões de documentos.

Este módulo oferece funcionalidades para:
- Enriquecer Markdown convertido pelo Docling com análise IA
- Extrair insights e sumários de documentos
- Melhorar formatação e estrutura
- Análise de conteúdo e classificação

Usa GPT-4o mini como modelo padrão para otimizar custos.
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import json

import openai
from openai import OpenAI

logger = logging.getLogger(__name__)

# Configurações padrão
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.3
DEFAULT_MAX_TOKENS = 2000

# Prompts especializados
MARKDOWN_ENHANCEMENT_PROMPT = """
Você é um especialista em análise e estruturação de documentos. 

Analise o seguinte conteúdo Markdown convertido de um documento e forneça melhorias:

1. **Estruturação**: Melhore a hierarquia de cabeçalhos e organização
2. **Formatação**: Corrija problemas de formatação Markdown
3. **Clareza**: Melhore a legibilidade mantendo o conteúdo original
4. **Metadados**: Extraia informações-chave (tipo de documento, temas principais, etc.)

Conteúdo original:
{content}

Retorne um JSON com:
- enhanced_markdown: versão melhorada do Markdown
- metadata: objeto com type, main_topics array, summary string
- improvements: array de melhorias aplicadas
"""

DOCUMENT_ANALYSIS_PROMPT = """
Analise o seguinte documento e forneça uma análise estruturada:

{content}

Retorne um JSON com:
- summary: resumo executivo em 2-3 frases
- key_points: array dos pontos principais
- document_type: tipo identificado do documento
- topics: array dos temas principais identificados  
- action_items: array de itens de ação se houver
- confidence: float entre 0 e 1 indicando confiança da análise
"""

CONTENT_EXTRACTION_PROMPT = """
Extraia as informações mais importantes do seguinte documento:

{content}

Foque em:
- Dados factuais
- Números e estatísticas
- Datas importantes
- Pessoas/organizações mencionadas
- Decisões ou conclusões

Retorne um JSON estruturado com as informações extraídas.
"""


class OpenAIEnhancer:
    """Cliente para enriquecer documentos usando OpenAI."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS
    ):
        """
        Inicializa o cliente OpenAI.
        
        Args:
            api_key: Chave da API OpenAI. Se None, usa OPENAI_API_KEY do ambiente
            model: Modelo a usar (padrão: gpt-4o-mini)
            temperature: Temperatura para geração (padrão: 0.3)
            max_tokens: Máximo de tokens na resposta (padrão: 2000)
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Configurar API key
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            # Usa OPENAI_API_KEY do ambiente
            self.client = OpenAI()
            
        logger.info(f"OpenAI Enhancer inicializado com modelo: {model}")
    
    def _make_request(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        """Faz uma requisição para a API OpenAI."""
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
                
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Requisição OpenAI concluída. Tokens usados: {response.usage.total_tokens}")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON da resposta OpenAI: {e}")
            return {"error": f"Erro de decodificação JSON: {str(e)}"}
        except Exception as e:
            logger.error(f"Erro na requisição OpenAI: {e}")
            return {"error": str(e)}
    
    def enhance_markdown(self, markdown_content: str) -> Dict[str, Any]:
        """
        Melhora um conteúdo Markdown usando IA.
        
        Args:
            markdown_content: Conteúdo Markdown original
            
        Returns:
            Dict com markdown melhorado, metadados e melhorias aplicadas
        """
        logger.info("Iniciando enriquecimento de Markdown com OpenAI")
        
        prompt = MARKDOWN_ENHANCEMENT_PROMPT.format(content=markdown_content)
        system_prompt = "Você é um especialista em estruturação de documentos. Sempre retorne JSON válido."
        
        result = self._make_request(prompt, system_prompt)
        
        if "error" in result:
            logger.error(f"Erro no enriquecimento: {result['error']}")
            return {
                "enhanced_markdown": markdown_content,  # Fallback para original
                "metadata": {"type": "unknown", "main_topics": [], "summary": "Erro na análise"},
                "improvements": [],
                "error": result["error"]
            }
        
        return result
    
    def analyze_document(self, content: str) -> Dict[str, Any]:
        """
        Analisa um documento e extrai insights.
        
        Args:
            content: Conteúdo do documento
            
        Returns:
            Dict com análise estruturada do documento
        """
        logger.info("Iniciando análise de documento com OpenAI")
        
        prompt = DOCUMENT_ANALYSIS_PROMPT.format(content=content)
        system_prompt = "Você é um analista de documentos experiente. Sempre retorne JSON válido."
        
        return self._make_request(prompt, system_prompt)
    
    def extract_key_information(self, content: str) -> Dict[str, Any]:
        """
        Extrai informações-chave de um documento.
        
        Args:
            content: Conteúdo do documento
            
        Returns:
            Dict com informações extraídas
        """
        logger.info("Iniciando extração de informações-chave com OpenAI")
        
        prompt = CONTENT_EXTRACTION_PROMPT.format(content=content)
        system_prompt = "Você é um especialista em extração de dados. Sempre retorne JSON válido."
        
        return self._make_request(prompt, system_prompt)
    
    def batch_enhance_documents(
        self, 
        documents: List[Dict[str, str]], 
        operation: str = "enhance"
    ) -> List[Dict[str, Any]]:
        """
        Processa múltiplos documentos em lote.
        
        Args:
            documents: Lista de dicts com 'path' e 'content'
            operation: Tipo de operação ('enhance', 'analyze', 'extract')
            
        Returns:
            Lista com resultados processados
        """
        logger.info(f"Processando lote de {len(documents)} documentos - operação: {operation}")
        
        results = []
        
        for i, doc in enumerate(documents):
            logger.info(f"Processando documento {i+1}/{len(documents)}: {doc.get('path', 'N/A')}")
            
            try:
                if operation == "enhance":
                    result = self.enhance_markdown(doc["content"])
                elif operation == "analyze":
                    result = self.analyze_document(doc["content"])
                elif operation == "extract":
                    result = self.extract_key_information(doc["content"])
                else:
                    raise ValueError(f"Operação inválida: {operation}")
                
                result["source_path"] = doc.get("path", "unknown")
                results.append(result)
                
            except Exception as e:
                logger.error(f"Erro processando documento {doc.get('path', 'N/A')}: {e}")
                results.append({
                    "source_path": doc.get("path", "unknown"),
                    "error": str(e)
                })
        
        return results


def create_enhancer_from_env() -> OpenAIEnhancer:
    """Cria um OpenAIEnhancer usando variáveis de ambiente."""
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
    temperature = float(os.getenv("OPENAI_TEMPERATURE", DEFAULT_TEMPERATURE))
    max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", DEFAULT_MAX_TOKENS))
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente")
    
    return OpenAIEnhancer(
        api_key=api_key,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )


# Função utilitária para uso direto
def enhance_markdown_content(content: str, api_key: str = None) -> Dict[str, Any]:
    """
    Função utilitária para melhorar conteúdo Markdown rapidamente.
    
    Args:
        content: Conteúdo Markdown
        api_key: Chave API OpenAI (opcional)
        
    Returns:
        Dict com resultado da melhoria
    """
    enhancer = OpenAIEnhancer(api_key=api_key)
    return enhancer.enhance_markdown(content)


if __name__ == "__main__":
    # Exemplo de uso
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste do OpenAI Enhancer")
    parser.add_argument("--test-content", help="Conteúdo de teste")
    parser.add_argument("--api-key", help="Chave API OpenAI")
    
    args = parser.parse_args()
    
    if args.test_content:
        try:
            result = enhance_markdown_content(args.test_content, args.api_key)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Erro: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Uso: python openai_enhancer.py --test-content 'Seu conteúdo aqui'")