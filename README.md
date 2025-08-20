# DOCLING

Projeto para converter arquivos em Markdown usando Docling no macOS (MacBook Air M3, 8GB RAM). Este repositório adota `uv` para gerenciar o ambiente Python e comandos não interativos com caminhos absolutos.

## Requisitos
- macOS com Homebrew
- Python 3.11+ (recomendado)
- `uv` para ambientes e dependências Python

## Instalação do `uv`
```bash
brew install uv
```

## Setup rápido
```bash
# criar ambiente isolado sem ativação manual
uv venv .venv

# instalar dependências (se existir requirements.txt)
uv pip install -r requirements.txt

# verificar Python
uv run python --version
```

## Estrutura recomendada
```
docling/
  scripts/
    convert.py      # script de conversão p/ Markdown (ex.: Docling)
  input/            # arquivos de entrada
  output/           # Markdown gerado
```

## Execução (exemplo)
Use caminhos absolutos e execução não interativa:
```bash
uv run python /Users/gabrielramos/docling/scripts/convert.py \
  --input /Users/gabrielramos/docling/input \
  --output /Users/gabrielramos/docling/output
```

## Boas práticas
- Prefira lotes pequenos para economizar memória.
- Evite carregar arquivos muito grandes inteiramente em memória.
- Use `logging` em vez de `print` em código de biblioteca.
- Anote funções públicas com type hints.

## Limpeza do ambiente
Ao finalizar o projeto e/ou arquivar o repositório, remova ambientes locais:
```bash
rm -rf .venv venv env
```

## Licença
Defina a licença do projeto (ex.: MIT) em `LICENSE`.