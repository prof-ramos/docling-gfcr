#!/usr/bin/env bash
set -euo pipefail

# Verifica dependências básicas
command -v uv >/dev/null 2>&1 || { echo "Erro: 'uv' não encontrado. Instale com 'brew install uv'"; exit 1; }

PROJECT_ROOT="/Users/gabrielramos/docling"
REQ_FILE="$PROJECT_ROOT/requirements.txt"

# Cria/atualiza ambiente e instala dependências
uv venv "$PROJECT_ROOT/.venv"
uv pip install -r "$REQ_FILE"

# Roda testes
uv run pytest -q --cov=scripts --cov-report=term-missing
