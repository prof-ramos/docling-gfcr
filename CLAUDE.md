# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment and Package Management

- **Python Environment**: Always use `uv` for Python package management and virtual environments
- **Virtual Environment**: `.venv` directory (created with `uv venv .venv`)
- **Dependencies**: Defined in `requirements.txt` - install with `uv pip install -r requirements.txt`
- **Python Version**: 3.11+ recommended
- **Platform**: Optimized for macOS (MacBook Air M3, 8GB RAM)

## Essential Commands

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
# Convert PDF to Markdown using absolute paths
uv run python scripts/convert.py --input /absolute/path/to/file.pdf

# Convert with JSON output
uv run python scripts/convert.py --input /path/to/file.pdf --json

# Output is automatically saved to /Users/gabrielramos/docling/output/
```

#### Claude Code Tool Usage
```bash
# Use as Claude Code tool via JSON stdin/stdout
echo '{"input_path": "/path/to/file.pdf", "return_content": true}' | uv run python scripts/claude_tool.py

# Test tool functionality
uv run pytest tests/test_claude_tool.py
```

## Architecture Overview

This is a document conversion tool that uses Docling as the primary converter with PyMuPDF as fallback:

### Core Components

- **`scripts/convert.py`**: Main conversion script with CLI interface
  - Primary: Uses Docling DocumentConverter for high-quality Markdown output  
  - Fallback: Uses PyMuPDF (fitz) for text extraction when Docling fails
  - Output: Always saves to fixed directory `/Users/gabrielramos/docling/output/`
  - Logging: Structured logging with INFO level for tracking conversion progress
  - New: `convert_document()` function for programmatic use
  - New: `--json` flag for JSON output format

- **`scripts/claude_tool.py`**: Claude Code tool interface
  - JSON Schema: Defines tool parameters and validation for Claude Code integration
  - stdin/stdout: Communicates via JSON for tool calling from Claude agents
  - Error handling: Comprehensive error reporting in JSON format
  - Flexible output: Supports both file saving and content return options

### Key Functions

- **`ensure_paths()`** - Validates input files and creates output directory structure
- **`convert_with_docling()`** - Attempts conversion using Docling API with error handling
- **`fallback_with_pymupdf()`** - Extracts raw text when Docling is unavailable
- **`convert_document()`** - Reusable conversion function returning structured results
- **`convert_document_tool()`** - Claude Code tool wrapper with parameter validation
- **`main()`** - CLI interface with argparse, processes conversion pipeline

### Testing Strategy

- **Unit tests**: Mock external dependencies (Docling, PyMuPDF) to test logic
- **CLI tests**: Test argument parsing and main workflow with monkeypatching
- **Tool tests**: Test Claude Code tool interface, JSON I/O, and schema validation
- **Coverage**: Focuses on `scripts/` module with term-missing reporting
- **Path handling**: Tests use `tmp_path` fixtures, but CLI tests verify fixed output paths

## File Structure

```
docling/
├── scripts/
│   ├── convert.py          # Main conversion logic with CLI and programmatic interfaces
│   ├── claude_tool.py      # Claude Code tool interface (JSON stdin/stdout)
│   ├── tool_config.json    # Tool configuration and schema for Claude Code
│   └── setup.sh           # Environment setup script
├── tests/
│   ├── test_cli.py        # CLI argument and workflow tests  
│   ├── test_convert.py    # Unit tests for conversion functions
│   └── test_claude_tool.py # Tests for Claude Code tool interface
├── output/                # Fixed output directory for converted files
├── requirements.txt       # Python dependencies
├── CLAUDE.md             # Claude Code integration guide
└── README.md             # Project documentation
```

## Development Patterns

- **Error Handling**: Graceful fallback from Docling to PyMuPDF with comprehensive error reporting
- **Path Management**: Uses `pathlib.Path` with absolute paths throughout
- **Memory Optimization**: Processes files individually, avoids loading large files entirely in memory
- **Non-interactive**: Designed for batch processing with complete file paths
- **Type Hints**: All public functions annotated with proper type hints
- **JSON Communication**: Structured data exchange for tool integration
- **Modular Design**: Separates CLI, programmatic, and tool interfaces

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
uv run python /Users/gabrielramos/docling/scripts/claude_tool.py
```

With JSON input like:
```json
{
  "input_path": "/path/to/document.pdf",
  "output_dir": "/custom/output/dir", 
  "return_content": true
}
```