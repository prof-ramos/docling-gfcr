# Manual de Integração - Agente de Conversão Markdown

Este manual fornece instruções completas para integrar e utilizar o sistema de conversão de documentos para Markdown, incluindo o agente especializado.

## 📋 Índice

- [Instalação e Configuração](#instalação-e-configuração)
- [Interfaces Disponíveis](#interfaces-disponíveis)
- [Agente Markdown Especializado](#agente-markdown-especializado)
- [Integração com Claude Code](#integração-com-claude-code)
- [Exemplos Práticos](#exemplos-práticos)
- [Troubleshooting](#troubleshooting)

## 🚀 Instalação e Configuração

### Pré-requisitos
- **macOS** com Homebrew
- **Python 3.11+** 
- **uv** para gerenciamento de pacotes

### Setup Inicial
```bash
# 1. Clonar o repositório
git clone https://github.com/prof-ramos/docling-gfcr.git
cd docling-gfcr

# 2. Executar setup automático
bash scripts/setup.sh

# 3. Verificar instalação
uv run pytest --cov=scripts --cov-report=term-missing
```

## 🔧 Interfaces Disponíveis

### 1. CLI Tradicional
```bash
# Conversão simples
uv run python scripts/convert.py --input /caminho/para/documento.pdf

# Com saída JSON
uv run python scripts/convert.py --input /caminho/para/documento.pdf --json
```

### 2. Tool para Claude Code
```bash
# Via JSON stdin/stdout
echo '{"input_path": "/caminho/documento.pdf", "return_content": true}' | \
uv run python scripts/claude_tool.py
```

### 3. Agente Markdown Especializado
```bash
# Conversão avançada com otimização e validação
echo '{"input_path": "/caminho/documento.pdf", "optimize": true, "validate": true}' | \
uv run python scripts/markdown_agent.py

# Conversão em lote
echo '{"input_path": ["/doc1.pdf", "/doc2.pdf"], "optimize": true}' | \
uv run python scripts/markdown_agent.py
```

## 🎯 Agente Markdown Especializado

### Características Principais

**📊 Análise Prévia:**
- Detecta formato e tamanho do arquivo
- Estima complexidade e número de páginas
- Valida compatibilidade com formatos suportados

**⚙️ Otimização Automática:**
- Adiciona metadados YAML frontmatter
- Limpa formatação excessiva (múltiplas quebras de linha)
- Melhora estrutura de cabeçalhos e listas
- Garante formatação consistente

**🔍 Validação de Qualidade:**
- Sistema de pontuação 0-100 pontos
- Métricas detalhadas (cabeçalhos, parágrafos, palavras)
- Identificação automática de problemas
- Relatório de qualidade estruturado

### Parâmetros de Configuração

```json
{
  "input_path": "string | string[]",  // Arquivo único ou lista para lote
  "output_dir": "string",             // Diretório de saída (opcional)
  "optimize": "boolean",              // Aplicar otimizações (padrão: true)
  "validate": "boolean",              // Executar validação (padrão: true)
  "return_content": "boolean"         // Retornar conteúdo na resposta (padrão: false)
}
```

### Exemplo de Resposta
```json
{
  "success": true,
  "agent": "markdown_agent",
  "input_analysis": {
    "filename": "documento.pdf",
    "size_mb": 2.5,
    "extension": ".pdf",
    "is_supported": true,
    "estimated_pages": 15
  },
  "conversion_method": "docling",
  "output_file": "/output/documento.md",
  "optimized": true,
  "validated": true,
  "validation": {
    "valid": true,
    "quality_score": 87,
    "metrics": {
      "headers_count": 12,
      "paragraphs_count": 45,
      "word_count": 1250,
      "char_count": 8500
    },
    "issues": []
  }
}
```

## 🔗 Integração com Claude Code

### Para Agentes Claude Code

**Prompt de Sistema:**
```
Você tem acesso a um agente especializado de conversão de documentos para Markdown. 
Use-o sempre que precisar converter PDFs, DOCs ou outros documentos.

Comando: uv run python /Users/gabrielramos/docling/scripts/markdown_agent.py
```

**Exemplo de Uso por Agente:**
```json
{
  "tool": "convert_document", 
  "parameters": {
    "input_path": "/caminho/para/arquivo.pdf",
    "optimize": true,
    "validate": true,
    "return_content": false
  }
}
```

### Configuração MCP (Model Context Protocol)

Para integrar via MCP, adicione ao `.mcp.json`:
```json
{
  "mcpServers": {
    "docling-converter": {
      "command": "uv",
      "args": [
        "run", 
        "python", 
        "/Users/gabrielramos/docling/scripts/markdown_agent.py"
      ],
      "cwd": "/Users/gabrielramos/docling"
    }
  }
}
```

## 💡 Exemplos Práticos

### 1. Conversão de Documentação Técnica
```bash
echo '{
  "input_path": "/docs/manual_usuario.pdf",
  "optimize": true,
  "validate": true,
  "return_content": true
}' | uv run python scripts/markdown_agent.py
```

### 2. Migração em Lote para Wiki
```bash
echo '{
  "input_path": [
    "/docs/capitulo1.pdf",
    "/docs/capitulo2.pdf", 
    "/docs/capitulo3.pdf"
  ],
  "output_dir": "/wiki/content",
  "optimize": true
}' | uv run python scripts/markdown_agent.py
```

### 3. Análise de Qualidade de Conversão
```bash
# Converter e validar qualidade
echo '{
  "input_path": "/reports/relatorio.pdf",
  "validate": true,
  "return_content": false
}' | uv run python scripts/markdown_agent.py | jq '.validation.quality_score'
```

## 🔧 Troubleshooting

### Problemas Comuns

**1. Erro de Dependências**
```bash
# Reinstalar ambiente
rm -rf .venv
bash scripts/setup.sh
```

**2. Arquivo Não Suportado**
- Verificar extensões suportadas: `.pdf`, `.docx`, `.doc`, `.txt`
- Confirmar que arquivo não está corrompido

**3. Falha na Conversão Docling**
- Sistema automaticamente usa fallback PyMuPDF
- Verificar logs para detalhes do erro

**4. Problemas de Permissão**
```bash
# Garantir permissões corretas
chmod +x scripts/*.py
chmod +x scripts/setup.sh
```

### Logs e Debugging

**Habilitar Logs Detalhados:**
```bash
export PYTHONPATH="/Users/gabrielramos/docling"
export LOG_LEVEL=DEBUG
uv run python scripts/markdown_agent.py
```

**Executar Testes Específicos:**
```bash
# Testar agente Markdown
uv run pytest tests/test_markdown_agent.py -v

# Testar integração Claude Code
uv run pytest tests/test_claude_tool.py -v

# Coverage completo
uv run pytest --cov=scripts --cov-report=html
```

## 📚 Recursos Adicionais

### Documentação Técnica
- `CLAUDE.md` - Guia para Claude Code
- `README.md` - Visão geral do projeto
- `scripts/markdown_agent_config.json` - Configuração completa

### Arquivos de Configuração
- `scripts/tool_config.json` - Schema para Claude Code tool
- `requirements.txt` - Dependências Python
- `.gitignore` - Arquivos excluídos do controle de versão

### Testes e Qualidade
- `tests/` - Suite de testes completa
- Coverage atual: **84%** (29/29 testes passando)
- Suporte a Python 3.11+ e macOS

## 📞 Suporte

Para problemas ou dúvidas:
1. Verificar logs de erro
2. Executar tests: `uv run pytest`
3. Consultar documentação técnica
4. Reportar issues no GitHub

---

**Versão:** 1.0.0  
**Última Atualização:** 20 agosto 2025  
**Compatibilidade:** macOS, Python 3.11+, uv package manager