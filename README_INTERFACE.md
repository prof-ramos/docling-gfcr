# 🚀 Interface UX - Conversor de Documentos

Interface moderna e intuitiva para conversão de documentos usando Docling.

## 🎯 Características

- **🌐 Interface Web**: Moderna e responsiva usando Streamlit
- **📤 Upload Drag & Drop**: Arraste arquivos diretamente para a interface
- **⚙️ Configurações Flexíveis**: Escolha formato e diretório de saída
- **📊 Feedback em Tempo Real**: Progresso visual e detalhes da conversão
- **💾 Download Direto**: Baixe arquivos convertidos diretamente da interface

## 📁 Extensões Suportadas

- **Documentos**: PDF, DOCX, XLSX, PPTX, HTML, XHTML, MD, CSV
- **Imagens**: PNG, JPEG, JPG, TIFF, TIF, BMP, WEBP
- **Especializados**: XML, JSON, ADOC, ASCIIDOC

## 🚀 Como Usar

### Método 1: Script Automático (Recomendado)
```bash
# Executa configuração e interface automaticamente
./run.sh
```

### Método 2: Manual
```bash
# 1. Instalar dependências
uv pip install -r requirements.txt

# 2. Executar interface web
uv run streamlit run scripts/web_ui.py
```

## 📋 Instruções da Interface

1. **📤 Upload**: 
   - Arraste o arquivo para a área de upload OU
   - Clique em "Browse files" para selecionar

2. **⚙️ Configurações**:
   - Escolha formato de saída (Markdown/Texto)
   - Habilite "Mostrar conteúdo na tela" para preview
   - Use diretório personalizado se necessário

3. **🔄 Conversão**:
   - Clique em "Converter Documento"
   - Acompanhe o progresso visual
   - Aguarde finalização

4. **📊 Resultado**:
   - Veja detalhes da conversão
   - Visualize conteúdo (se habilitado)
   - Download direto do arquivo convertido

## 🛠️ Arquitetura

### Arquivos da Interface
```
scripts/
├── web_ui.py          # Interface web principal (Streamlit)
├── gui.py             # Interface desktop (Tkinter) - alternativa
├── convert.py         # Engine de conversão
└── claude_tool.py     # Interface para Claude Code
```

### Script de Execução
```
run.sh                 # Script principal com configuração automática
```

## 🎨 Interface Web - Screenshots Conceituais

### Tela Principal
```
╔══════════════════════════════════════════════════════════════╗
║                 🔄 Conversor de Documentos                   ║
║                  Interface Web - Powered by Docling         ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📤 Upload do Arquivo                    ⚙️ Configurações    ║
║  ┌─────────────────────────────────┐    ┌─────────────────┐ ║
║  │  Arraste arquivo aqui ou        │    │ Formato: MD     │ ║
║  │      clique para selecionar     │    │ □ Mostrar tela  │ ║
║  │                                 │    │ □ Dir. custom   │ ║
║  └─────────────────────────────────┘    └─────────────────┘ ║
║                                                              ║
║              🔄 [Converter Documento]                        ║
║                                                              ║
║  📊 Resultado da Conversão                                   ║
║  ✅ Conversão Realizada com Sucesso!                        ║
║  Método: docling | Tamanho: 291,747 bytes                  ║
║  💾 [Download] 📋 [Copiar Caminho]                          ║
╚══════════════════════════════════════════════════════════════╝
```

## 🔧 Configurações Avançadas

### Variáveis de Ambiente
```bash
# Diretório padrão de saída
export DOCLING_OUTPUT_DIR="/caminho/personalizado"

# Porta da interface web (padrão: 8501)
export STREAMLIT_SERVER_PORT=8080
```

### Personalização do run.sh
O script detecta automaticamente:
- ✅ Python 3 e uv instalados
- ✅ Ambiente virtual (.venv)
- ✅ Dependências necessárias
- ✅ Diretório de output
- ✅ Permissões de escrita

## ⚡ Performance

- **Processamento**: Thread separada para não bloquear UI
- **Upload**: Arquivos temporários gerenciados automaticamente
- **Memória**: Limpeza automática após conversão
- **Cache**: Streamlit otimiza re-renderizações

## 🐛 Resolução de Problemas

### Interface não abre
```bash
# Verificar se porta está livre
lsof -i :8501

# Usar porta alternativa
uv run streamlit run scripts/web_ui.py --server.port=8502
```

### Erro de dependências
```bash
# Reinstalar ambiente limpo
rm -rf .venv
uv venv .venv
uv pip install -r requirements.txt
```

### Tkinter não funciona (GUI alternativa)
```bash
# macOS
brew install python-tk

# Ubuntu/Debian
sudo apt-get install python3-tk
```

## 🎯 Próximas Melhorias

- [ ] **Processamento em lote**: Upload múltiplo
- [ ] **Histórico**: Lista de conversões anteriores
- [ ] **Preview**: Visualização prévia de arquivos
- [ ] **Temas**: Dark/Light mode
- [ ] **API**: Endpoint REST para integração

## 📞 Suporte

Para usar a **interface CLI** tradicional:
```bash
uv run python scripts/convert.py --input "arquivo.pdf" --json
```

Para integração com **Claude Code**:
```bash
echo '{"input_path": "arquivo.pdf"}' | uv run python scripts/claude_tool.py
```