#!/bin/bash

# Conversor de Documentos - Script de Execução
# Este script configura o ambiente e executa a interface gráfica

set -e  # Sair em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

# Banner
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                  CONVERSOR DE DOCUMENTOS                     ║"
echo "║                     Interface Gráfica                        ║"
echo "║                                                               ║"
echo "║  Suporte: PDF, DOCX, XLSX, PPTX, HTML, MD, CSV, Imagens     ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar se estamos no diretório correto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

print_status "Diretório do projeto: $PROJECT_ROOT"

# Navegar para o diretório do projeto
cd "$PROJECT_ROOT"

# Verificar se o Python está disponível
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 não encontrado. Por favor, instale o Python 3."
    exit 1
fi

print_success "Python 3 encontrado: $(python3 --version)"

# Verificar se uv está disponível
if ! command -v uv &> /dev/null; then
    print_error "uv não encontrado. Por favor, instale o uv:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

print_success "uv encontrado: $(uv --version)"

# Verificar se o ambiente virtual existe
if [ ! -d ".venv" ]; then
    print_warning "Ambiente virtual não encontrado. Criando..."
    uv venv .venv
    print_success "Ambiente virtual criado"
fi

# Verificar se as dependências estão instaladas
print_status "Verificando dependências..."
if ! uv run python -c "import docling" &> /dev/null; then
    print_warning "Dependências não instaladas. Instalando..."
    uv pip install -r requirements.txt
    print_success "Dependências instaladas"
else
    print_success "Dependências já instaladas"
fi

# Verificar se Streamlit está disponível (necessário para interface web)
print_status "Verificando suporte à interface web..."
if ! uv run python -c "import streamlit" &> /dev/null; then
    print_warning "Streamlit não encontrado. Instalando..."
    uv pip install streamlit
    print_success "Streamlit instalado"
else
    print_success "Interface web disponível"
fi

# Criar diretório de output se não existir
OUTPUT_DIR="/Users/gabrielramos/docling/output"
if [ ! -d "$OUTPUT_DIR" ]; then
    print_status "Criando diretório de output: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
    print_success "Diretório de output criado"
fi

# Verificar permissões de escrita no diretório de output
if [ ! -w "$OUTPUT_DIR" ]; then
    print_error "Sem permissão de escrita no diretório: $OUTPUT_DIR"
    print_warning "Você pode escolher outro diretório na interface"
fi

# Função de limpeza em caso de interrupção
cleanup() {
    print_warning "Execução interrompida pelo usuário"
    exit 1
}

trap cleanup SIGINT SIGTERM

# Executar a interface web
print_status "Iniciando interface web..."
echo ""
print_status "📋 Como usar:"
print_status "  1. A interface será aberta no seu navegador"
print_status "  2. Faça upload do arquivo arrastando ou clicando"
print_status "  3. Configure as opções de saída"
print_status "  4. Clique em 'Converter Documento'"
echo ""
print_status "💡 Dica: A interface ficará disponível em http://localhost:8501"
echo ""

# Executar a interface web
if uv run streamlit run scripts/web_ui.py --server.port=8501 --server.headless=false; then
    print_success "Interface web encerrada normalmente"
else
    exit_code=$?
    print_error "Erro na execução da interface web (código: $exit_code)"
    
    # Sugerir alternativa CLI
    echo ""
    print_status "💡 Alternativa: Use a versão linha de comando:"
    echo "  uv run python scripts/convert.py --input 'caminho/para/arquivo.pdf'"
    
    exit $exit_code
fi