# Docling Advanced Converter

Sistema avançado de conversão de documentos para Markdown com agente especializado, integração Claude Code e funcionalidades de otimização e validação de qualidade.

## 🚀 Características Principais

- **🔄 Conversão Inteligente**: Docling (primário) + PyMuPDF (fallback)
- **🤖 Agente Especializado**: MarkdownAgent com análise, otimização e validação
- **🔗 Integração Claude Code**: Tool interface para agentes IA
- **📊 Validação de Qualidade**: Sistema de pontuação 0-100 com métricas detalhadas
- **⚡ Processamento em Lote**: Múltiplos arquivos simultaneamente
- **🎯 Formatos Suportados**: PDF, DOCX, DOC, TXT

## 📋 Requisitos

- **macOS** com Homebrew
- **Python 3.11+**
- **uv** para gerenciamento de pacotes
- **8GB RAM** recomendado

## ⚡ Setup Rápido

```bash
# 1. Instalar uv
brew install uv

# 2. Setup automático
bash scripts/setup.sh

# 3. Testar instalação
uv run pytest --cov=scripts
```

## 🔧 Interfaces de Uso

### 1. CLI Tradicional
```bash
# Conversão básica
uv run python scripts/convert.py --input documento.pdf

# Com saída JSON
uv run python scripts/convert.py --input documento.pdf --json
```

### 2. Agente Markdown Especializado
```bash
# Conversão com otimização e validação
echo '{"input_path": "documento.pdf", "optimize": true, "validate": true}' | \
uv run python scripts/markdown_agent.py

# Processamento em lote
echo '{"input_path": ["doc1.pdf", "doc2.pdf"], "optimize": true}' | \
uv run python scripts/markdown_agent.py
```

### 3. Tool para Claude Code
```bash
# Interface para agentes IA
echo '{"input_path": "documento.pdf", "return_content": true}' | \
uv run python scripts/claude_tool.py
```

## 🎯 Agente Markdown - Funcionalidades

### Análise Prévia
- ✅ Detecção automática de formato
- ✅ Análise de tamanho e complexidade
- ✅ Estimativa de páginas
- ✅ Validação de compatibilidade

### Otimização Automática
- ✅ Metadados YAML frontmatter
- ✅ Limpeza de formatação excessiva
- ✅ Estruturação de cabeçalhos
- ✅ Formatação de listas

### Validação de Qualidade
- ✅ Pontuação 0-100
- ✅ Métricas detalhadas (cabeçalhos, parágrafos, palavras)
- ✅ Identificação de problemas
- ✅ Relatório estruturado

## 📊 Estrutura do Projeto

```
docling/
├── scripts/
│   ├── convert.py                    # Conversão principal + CLI
│   ├── markdown_agent.py             # Agente especializado
│   ├── claude_tool.py                # Interface Claude Code
│   ├── tool_config.json              # Configuração tool
│   ├── markdown_agent_config.json    # Configuração agente
│   └── setup.sh                     # Setup automático
├── tests/
│   ├── test_convert.py              # Testes conversão
│   ├── test_markdown_agent.py       # Testes agente
│   └── test_claude_tool.py          # Testes tool
├── output/                          # Arquivos convertidos
├── MANUAL_INTEGRACAO.md            # Manual completo
├── PROMPT_INTEGRACAO.md            # Prompts para IA
├── CLAUDE.md                       # Guia Claude Code
└── README.md                       # Este arquivo
```

## 🧪 Qualidade e Testes

- ✅ **29 testes** todos passando
- ✅ **84% cobertura** de código
- ✅ **CI/CD** configurado
- ✅ **Type hints** completos
- ✅ **Documentação** abrangente

```bash
# Executar todos os testes
uv run pytest

# Com coverage
uv run pytest --cov=scripts --cov-report=term-missing

# Teste específico do agente
uv run pytest tests/test_markdown_agent.py -v
```

## 🔗 Integração

### Para Agentes Claude Code
```json
{
  "tool": "markdown_converter",
  "command": "uv run python /Users/gabrielramos/docling/scripts/markdown_agent.py",
  "schema": {
    "input_path": "string|array",
    "optimize": "boolean",
    "validate": "boolean"
  }
}
```

### Para MCP (Model Context Protocol)
```json
{
  "mcpServers": {
    "docling": {
      "command": "uv",
      "args": ["run", "python", "/path/to/docling/scripts/markdown_agent.py"]
    }
  }
}
```

## 📚 Documentação

- **[Manual de Integração](MANUAL_INTEGRACAO.md)** - Guia completo de uso
- **[Prompts de Integração](PROMPT_INTEGRACAO.md)** - Prompts para IA
- **[Claude Code Guide](CLAUDE.md)** - Especificamente para Claude Code
- **[Configurações](scripts/)** - Arquivos JSON com exemplos

## 💡 Casos de Uso

- **📚 Migração de Documentação** para wikis e CMS
- **📄 Processamento de Relatórios** PDF automatizado
- **🎓 Conversão de Material Educativo** 
- **⚖️ Documentos Legais** com preservação de estrutura
- **🔄 Workflows de Automação** com validação de qualidade

## 🛠️ Desenvolvimento

### Comandos Úteis
```bash
# Ambiente de desenvolvimento
uv venv .venv
source .venv/bin/activate  # se necessário

# Testes rápidos
uv run pytest tests/test_markdown_agent.py::test_convert_document_success

# Debugging
export LOG_LEVEL=DEBUG
uv run python scripts/markdown_agent.py
```

### Contribuição
1. Fork do repositório
2. Criar branch feature
3. Implementar com testes
4. Coverage mínimo 80%
5. Pull request com descrição

## 🔧 Troubleshooting

### Problemas Comuns

**Dependências:**
```bash
rm -rf .venv
bash scripts/setup.sh
```

**Permissões:**
```bash
chmod +x scripts/*.py
```

**Logs:**
```bash
export PYTHONPATH="/Users/gabrielramos/docling"
uv run python scripts/markdown_agent.py
```

## 📈 Performance

- **Memória**: Otimizado para arquivos grandes
- **Velocidade**: Processamento paralelo em lotes
- **Qualidade**: Fallback automático garante conversão
- **Monitoramento**: Métricas detalhadas de qualidade

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

**Versão**: 1.0.0 | **Última atualização**: Agosto 2025 | **Compatibilidade**: macOS, Python 3.11+

🤖 **Desenvolvido com [Claude Code](https://claude.ai/code)**