# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment and Package Management

- **Python Environment**: Always use `uv` for Python package management and virtual environments
- **Virtual Environment**: `.venv` directory (created with `uv venv .venv`)
- **Dependencies**: Defined in `requirements.txt` - install with `uv pip install -r requirements.txt`
- **Python Version**: 3.11+ recommended
- **Platform**: Optimized for macOS (MacBook Air M3, 8GB RAM)
- **Memory Considerations**: Process files individually, avoid loading large files entirely in memory

## Essential Commands

### Quick Start with GPT-4o-mini
```bash
# Setup completo com teste de OpenAI
bash scripts/setup.sh
export OPENAI_API_KEY="your-api-key-here"
uv run python scripts/convert.py --input sample.pdf --enhance
```

### Setup and Installation
```bash
# Setup environment and install dependencies
bash scripts/setup.sh

# Manual setup if needed
uv venv .venv
uv pip install -r requirements.txt
```

### Testing
```bash
# Run all tests with coverage
uv run pytest -q --cov=scripts --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_cli.py
uv run pytest tests/test_convert.py
uv run pytest tests/test_claude_tool.py

# Run single test
uv run pytest tests/test_cli.py::test_cli_requires_input
```

### Document Conversion

#### CLI Usage
```bash
# Convert single document to Markdown using absolute paths
uv run python scripts/convert.py --input /absolute/path/to/file.pdf

# Convert with JSON output format
uv run python scripts/convert.py --input /path/to/file.pdf --json

# Output is automatically saved to /Users/gabrielramos/docling/output/
```

#### Web Interface
```bash
# Launch modern Streamlit web interface
bash run.sh

# Or directly launch web UI
uv run streamlit run scripts/web_ui.py --server.port=8501
```

#### Claude Code Tool Usage
```bash
# Conversão básica via tool
echo '{"input_path": "/path/to/file.pdf", "return_content": true}' | uv run python scripts/claude_tool.py

# Conversão com enriquecimento GPT-4o-mini
echo '{"input_path": "/path/to/file.pdf", "enhance_with_openai": true, "return_content": true}' | uv run python scripts/claude_tool.py

# Test tool functionality
uv run pytest tests/test_claude_tool.py
```

#### Markdown Agent (Specialized)
```bash
# Use specialized Markdown agent with advanced features
echo '{"input_path": "/path/to/file.pdf", "optimize": true, "validate": true}' | uv run python scripts/markdown_agent.py

# Batch conversion with Markdown agent
echo '{"input_path": ["/path/file1.pdf", "/path/file2.pdf"], "optimize": true}' | uv run python scripts/markdown_agent.py

# Test Markdown agent
uv run pytest tests/test_markdown_agent.py
```

## Architecture Overview

Este é um sistema avançado de conversão de documentos que utiliza múltiplas interfaces:

- **Core Engine**: Docling (primário) + PyMuPDF (fallback)
- **Interfaces**: CLI, Web UI (Streamlit), Agente Especializado, Tool para Claude Code
- **Formatos Suportados**: PDF, DOCX, XLSX, PPTX, HTML, MD, CSV, imagens (PNG, JPEG, etc.)
- **OpenAI Integration**: Funcionalidade de enriquecimento de conteúdo com `openai_enhancer.py`

### Core Components

- **`scripts/convert.py`**: Main conversion script with CLI interface
  - Primary: Uses Docling DocumentConverter for high-quality Markdown output  
  - Fallback: Uses PyMuPDF (fitz) for text extraction when Docling fails
  - Output: Always saves to fixed directory `/Users/gabrielramos/docling/output/`
  - Logging: Structured logging with INFO level for tracking conversion progress
  - `convert_document()` function for programmatic use
  - `--json` flag for JSON output format
  - OpenAI integration support for content enhancement

- **`scripts/web_ui.py`**: Modern Streamlit web interface
  - File upload via drag-and-drop or browse
  - Real-time conversion progress
  - Responsive design with CSS customization
  - Automatic output directory management
  - Error handling with user-friendly messages

- **`scripts/claude_tool.py`**: Claude Code tool interface
  - JSON Schema: Defines tool parameters and validation for Claude Code integration
  - stdin/stdout: Communicates via JSON for tool calling from Claude agents
  - Error handling: Comprehensive error reporting in JSON format
  - Flexible output: Supports both file saving and content return options

- **`scripts/markdown_agent.py`**: Specialized Markdown conversion agent
  - Advanced Features: Document analysis, Markdown optimization, quality validation
  - Batch Processing: Support for multiple files in single operation
  - Quality Metrics: Automated assessment of conversion quality with scoring (0-100)
  - Metadata Enhancement: Adds YAML frontmatter and optimizes structure
  - JSON Schema validation for input parameters

- **`scripts/openai_enhancer.py`**: GPT-4o-mini integration para enriquecimento
  - **Modelo padrão**: GPT-4o-mini para otimização de custos
  - **3 operações principais**: enhance (melhoria), analyze (análise), extract (extração)
  - **Prompts especializados**: Para diferentes tipos de processamento
  - **Batch processing**: Suporte a múltiplos documentos
  - **JSON response format**: Saída estruturada garantida
  - **Fallback graceful**: Funciona mesmo sem API key configurada
  - **Token monitoring**: Tracking de uso de tokens da API
  - **Environment configuration**: Configuração via variáveis de ambiente

### Key Functions

**Core Conversion:**
- **`ensure_paths()`** - Validates input files and creates output directory structure
- **`convert_with_docling()`** - Attempts conversion using Docling API with error handling
- **`fallback_with_pymupdf()`** - Extracts raw text when Docling is unavailable
- **`convert_document()`** - Reusable conversion function returning structured results

**Tool Interfaces:**
- **`convert_document_tool()`** - Claude Code tool wrapper with parameter validation
- **`main()`** - CLI interface with argparse, processes conversion pipeline

**Markdown Agent Specialized:**
- **`MarkdownAgent.analyze_document()`** - Pre-conversion document analysis
- **`MarkdownAgent.optimize_markdown()`** - Post-conversion optimization and formatting
- **`MarkdownAgent.validate_markdown()`** - Quality assessment with detailed metrics
- **`MarkdownAgent.batch_convert()`** - Multi-file processing with progress tracking

### Testing Strategy

- **Unit tests**: Mock external dependencies (Docling, PyMuPDF) to test logic
- **CLI tests**: Test argument parsing and main workflow with monkeypatching
- **Tool tests**: Test Claude Code tool interface, JSON I/O, and schema validation
- **Agent tests**: Test Markdown agent features (analysis, optimization, validation, batch processing)
- **Coverage**: Focuses on `scripts/` module with term-missing reporting
- **Path handling**: Tests use `tmp_path` fixtures, but CLI tests verify fixed output paths

## File Structure

```
docling-gfcr/
├── scripts/
│   ├── convert.py                    # Main conversion logic with CLI and programmatic interfaces
│   ├── claude_tool.py                # Claude Code tool interface (JSON stdin/stdout)
│   ├── markdown_agent.py             # Specialized Markdown conversion agent
│   ├── web_ui.py                     # Modern Streamlit web interface
│   ├── openai_enhancer.py            # OpenAI content enhancement integration
│   ├── tool_config.json              # Tool configuration and schema for Claude Code
│   ├── markdown_agent_config.json    # Markdown agent configuration and examples
│   └── setup.sh                     # Environment setup script
├── tests/
│   ├── test_cli.py                  # CLI argument and workflow tests  
│   ├── test_convert.py              # Unit tests for conversion functions
│   ├── test_claude_tool.py          # Tests for Claude Code tool interface
│   └── test_markdown_agent.py       # Tests for Markdown agent functionality
├── .cursor/rules/                   # Cursor IDE configuration rules
├── output/                          # Fixed output directory for converted files
├── run.sh                          # Web interface launcher script
├── requirements.txt                 # Python dependencies
├── CLAUDE.md                       # Claude Code integration guide
├── README.md                       # Project documentation
├── MANUAL_INTEGRACAO.md            # Integration manual
└── PROMPT_INTEGRACAO.md            # AI integration prompts
```

## GPT-4o-mini Workflow Integration

### Pipeline de Conversão Completo
```
1. Input Document (PDF, DOCX, etc.)
   ↓
2. Docling Conversion → Markdown Base
   ↓
3. [OPCIONAL] GPT-4o-mini Enhancement:
   - Análise de estrutura
   - Melhoria de formatação
   - Extração de metadados
   - Geração de insights
   ↓
4. Output Final + Metadados
```

### Classes e Métodos Principais
- **`OpenAIEnhancer`**: Classe principal para integração
  - `enhance_markdown()`: Melhora Markdown convertido
  - `analyze_document()`: Análise completa do documento
  - `extract_key_information()`: Extração de dados factuais
  - `batch_enhance_documents()`: Processamento em lote

### Prompts Especializados
- **MARKDOWN_ENHANCEMENT_PROMPT**: Melhoria de estrutura e formatação
- **DOCUMENT_ANALYSIS_PROMPT**: Análise completa com insights
- **CONTENT_EXTRACTION_PROMPT**: Extração de informações-chave

## Development Patterns and Code Style

### Core Patterns
- **Error Handling**: Graceful fallback from Docling to PyMuPDF with comprehensive error reporting
- **Path Management**: Uses `pathlib.Path` with absolute paths throughout
- **Memory Optimization**: Processes files individually, avoids loading large files entirely in memory
- **Non-interactive**: Designed for batch processing with complete file paths
- **Type Hints**: All public functions annotated with proper type hints
- **JSON Communication**: Structured data exchange for tool integration
- **Modular Design**: Separates CLI, web UI, programmatic, and tool interfaces

### Python Style Guidelines (from .cursor/rules)
- **Type Annotations**: Annotate public function signatures; avoid unnecessary `Any`
- **Naming**: Use descriptive complete names; avoid cryptic abbreviations
- **Control Flow**: Prefer guard clauses; handle errors and edge cases early
- **Exceptions**: Don't catch exceptions without handling them; avoid bare `except`
- **Logging**: Use `logging` module with appropriate levels; avoid `print` in library code
- **Testing**: Write pure functions when possible; minimize side effects; inject dependencies

## Claude Code Tool Integration

This project includes a specialized tool interface (`scripts/claude_tool.py`) that enables Claude Code agents to use the document conversion functionality. The tool:

- **JSON Schema Validation**: Uses predefined schema for parameter validation
- **stdin/stdout Communication**: Reads JSON parameters from stdin, outputs results to stdout  
- **Error Resilience**: Comprehensive error handling with structured JSON responses
- **Flexible Output**: Can save files only or return content in the response
- **Configuration**: `scripts/tool_config.json` contains complete tool definition and examples

### Tool Usage for Claude Code Agents

When Claude Code agents need to convert documents, they can invoke:
```bash
uv run python /Users/gabrielramos/docling-gfcr/scripts/claude_tool.py
```

#### Basic Conversion
```json
{
  "input_path": "/path/to/document.pdf",
  "output_dir": "/custom/output/dir", 
  "return_content": true
}
```

#### Enhanced Conversion with GPT-4o-mini
```json
{
  "input_path": "/path/to/document.pdf",
  "output_dir": "/custom/output/dir",
  "return_content": true,
  "enhance_with_openai": true
}
```

### Response Format (Enhanced)
```json
{
  "status": "success",
  "input_path": "/path/to/document.pdf",
  "output_files": {
    "markdown": "/output/document.md",
    "json": "/output/document.json"
  },
  "content": "# Enhanced Markdown Content...",
  "conversion_info": {
    "method": "docling+openai",
    "processing_time": 12.34,
    "pages_processed": 15
  },
  "openai_enhancement": {
    "applied": true,
    "metadata": {
      "type": "technical_report",
      "main_topics": ["analysis", "performance"],
      "summary": "Technical performance analysis report"
    },
    "improvements": ["Header restructuring", "List formatting", "Metadata extraction"]
  }
}
```

## Additional Features

### GPT-4o-mini Integration & Enhancement Workflow

O sistema integra GPT-4o-mini para enriquecimento inteligente de conversões:

#### Configuração
```bash
# Configurar chave API OpenAI
export OPENAI_API_KEY="your-api-key"

# Configurações opcionais
export OPENAI_MODEL="gpt-4o-mini"           # Padrão: gpt-4o-mini
export OPENAI_TEMPERATURE="0.3"             # Padrão: 0.3
export OPENAI_MAX_TOKENS="2000"             # Padrão: 2000
```

#### Uso CLI com Enhancement
```bash
# Conversão com melhoria IA
uv run python scripts/convert.py --input document.pdf --enhance

# Teste do enhancer independente
uv run python scripts/openai_enhancer.py --test-content "# Markdown content"
```

#### Funcionalidades do GPT-4o-mini
1. **Enhance Markdown**: Melhora estrutura e formatação
2. **Document Analysis**: Extrai insights e metadados
3. **Key Information**: Identifica dados factuais importantes
4. **Batch Processing**: Processa múltiplos documentos

#### Exemplo de Output Enriquecido
```json
{
  "enhanced_markdown": "# Título Melhorado\n\n## Seções Organizadas...",
  "metadata": {
    "type": "relatório_técnico",
    "main_topics": ["análise", "performance"],
    "summary": "Relatório sobre performance do sistema"
  },
  "improvements": ["Estruturação de cabeçalhos", "Formatação de listas"]
}
```

### Performance Monitoring
- **Log Levels**: Set `LOG_LEVEL=DEBUG` for detailed operation tracking
- **Coverage Reports**: Always run tests with coverage reporting
- **Memory Usage**: Monitor with Activity Monitor on macOS for large file processing

### Troubleshooting

#### Ambiente e Dependências
```bash
# Clean environment and reinstall
rm -rf .venv
bash scripts/setup.sh

# Check core dependencies
uv run python -c "import docling; print('Docling OK')"
uv run python -c "import streamlit; print('Streamlit OK')"

# Check OpenAI integration
uv run python -c "import openai; print('OpenAI OK')"

# Debug path issues
export PYTHONPATH="/Users/gabrielramos/docling-gfcr"
```

#### GPT-4o-mini Issues
```bash
# Test OpenAI connection
export OPENAI_API_KEY="your-key"
uv run python scripts/openai_enhancer.py --test-content "# Test content"

# Check API key
echo $OPENAI_API_KEY

# Verify model access
uv run python -c "from scripts.openai_enhancer import create_enhancer_from_env; e = create_enhancer_from_env(); print('GPT-4o-mini OK')"

# Test with fallback (without enhancement)
uv run python scripts/convert.py --input document.pdf  # Sem --enhance
```

#### Error Handling
- **API Key Missing**: Conversão funciona normalmente sem enriquecimento
- **Rate Limits**: Sistema faz fallback para Markdown básico
- **Model Errors**: Logs detalhados em stderr para debugging
- **Token Limits**: Conteúdo é truncado automaticamente