# Prompts para Integração do Agente de Conversão Markdown

Este arquivo contém prompts prontos para integrar o sistema de conversão de documentos com agentes Claude Code e outros sistemas de IA.

## 🎯 Prompt para Agentes Claude Code

### Prompt de Sistema Base
```
SISTEMA DE CONVERSÃO DE DOCUMENTOS

Você tem acesso a um agente especializado de conversão de documentos para Markdown de alta qualidade. 

COMANDO: uv run python /Users/gabrielramos/docling/scripts/markdown_agent.py

CAPACIDADES:
- Converte PDF, DOCX, DOC, TXT para Markdown
- Análise prévia de documentos (tamanho, formato, páginas estimadas)  
- Otimização automática (metadados YAML, estrutura, formatação)
- Validação de qualidade com pontuação 0-100
- Processamento em lote de múltiplos arquivos
- Fallback automático Docling → PyMuPDF

QUANDO USAR:
- Sempre que o usuário mencionar conversão de documentos
- Para migrar documentação existente
- Ao processar PDFs ou documentos Word
- Para análise de qualidade de conversões

FORMATO DE ENTRADA JSON:
{
  "input_path": "caminho_arquivo_ou_lista",
  "optimize": true,
  "validate": true, 
  "return_content": false
}
```

### Prompt para Tarefas Específicas

**Conversão de Documentação:**
```
Quando o usuário solicitar conversão de documentação, use o agente especializado:

1. Identifique os arquivos a converter
2. Configure otimização=true para melhor qualidade
3. Configure validate=true para métricas de qualidade
4. Use return_content=true se precisar mostrar resultado
5. Para múltiplos arquivos, use array no input_path

Sempre explique as métricas de qualidade retornadas.
```

**Migração para Wiki/CMS:**
```
Para migração de documentos para wikis ou CMS:

1. Use processamento em lote para eficiência
2. Configure output_dir personalizado se necessário
3. Ative otimização para melhor formatação
4. Valide qualidade e reporte problemas encontrados
5. Forneça resumo dos sucessos/falhas
```

## 🔧 Prompts para Sistemas MCP

### Configuração MCP Server
```json
{
  "name": "docling_markdown_agent",
  "description": "Agente especializado em conversão de documentos para Markdown",
  "command": "uv",
  "args": ["run", "python", "/Users/gabrielramos/docling/scripts/markdown_agent.py"],
  "cwd": "/Users/gabrielramos/docling",
  "schema": {
    "input_path": {"type": "string|array", "required": true},
    "optimize": {"type": "boolean", "default": true},
    "validate": {"type": "boolean", "default": true},
    "return_content": {"type": "boolean", "default": false}
  }
}
```

## 🤖 Prompts para Automação

### Script de Automação
```bash
#!/bin/bash
# Prompt para automação de conversão em lote

convert_documents() {
    local input_dir="$1"
    local output_dir="$2"
    
    # Encontrar todos os PDFs
    find "$input_dir" -name "*.pdf" -print0 | \
    while IFS= read -r -d '' file; do
        echo "Convertendo: $file"
        
        echo "{
            \"input_path\": \"$file\",
            \"output_dir\": \"$output_dir\",
            \"optimize\": true,
            \"validate\": true
        }" | uv run python /Users/gabrielramos/docling/scripts/markdown_agent.py
    done
}

# Uso: convert_documents "/docs/input" "/docs/output"
```

## 📊 Prompt para Análise de Qualidade

### Análise Automática
```
ANÁLISE DE QUALIDADE DE CONVERSÕES

Para cada documento convertido, analise:

1. PONTUAÇÃO DE QUALIDADE:
   - 90-100: Excelente (estrutura perfeita)
   - 70-89: Boa (pequenos ajustes necessários)  
   - 50-69: Regular (melhorias recomendadas)
   - <50: Ruim (revisão manual necessária)

2. MÉTRICAS A AVALIAR:
   - Número de cabeçalhos (estrutura)
   - Contagem de parágrafos (conteúdo)
   - Total de palavras (completude)
   - Issues identificados (problemas)

3. RECOMENDAÇÕES:
   - Se score < 70: sugerir revisão manual
   - Se sem cabeçalhos: documento pode precisar estruturação
   - Se poucos parágrafos: verificar se conversão foi completa

Sempre forneça interpretação humana das métricas.
```

## 🔄 Prompts para Workflow Integrado

### Workflow Completo
```
WORKFLOW DE CONVERSÃO DE DOCUMENTOS

1. RECEPÇÃO:
   - Identificar tipo de documento
   - Validar formato suportado (.pdf, .docx, .doc, .txt)
   - Confirmar localização do arquivo

2. PRÉ-PROCESSAMENTO:
   - Analisar tamanho e complexidade
   - Decidir se usar conversão única ou lote
   - Configurar parâmetros otimais

3. CONVERSÃO:
   - Executar agente Markdown com otimização
   - Monitorar método usado (Docling vs PyMuPDF)
   - Capturar métricas de qualidade

4. PÓS-PROCESSAMENTO:
   - Avaliar score de qualidade
   - Identificar e reportar issues
   - Sugerir melhorias se necessário

5. ENTREGA:
   - Confirmar criação do arquivo de saída
   - Fornecer resumo da conversão
   - Disponibilizar conteúdo se solicitado
```

### Tratamento de Erros
```
TRATAMENTO DE ERROS NA CONVERSÃO

ERROS COMUNS:
1. "Arquivo não encontrado"
   → Verificar caminho e permissões
   
2. "Formato não suportado"  
   → Listar formatos suportados e sugerir alternativas
   
3. "Falha na conversão Docling"
   → Informar que fallback PyMuPDF foi usado
   
4. "Baixa qualidade (score < 50)"
   → Sugerir conversão manual ou arquivo diferente

SEMPRE:
- Explicar o erro de forma clara
- Oferecer soluções alternativas  
- Mostrar logs relevantes se disponíveis
- Orientar próximos passos
```

## 📈 Prompts para Monitoramento

### Métricas de Performance
```
MONITORAMENTO DO AGENTE DE CONVERSÃO

RASTREIE:
1. Taxa de sucesso das conversões
2. Tempo médio de processamento
3. Distribuição dos scores de qualidade
4. Uso de Docling vs PyMuPDF fallback
5. Tipos de documentos mais processados

ALERTAS CONFIGURAR:
- Score médio < 70 (qualidade baixa)
- Taxa de fallback > 30% (problemas Docling)
- Falhas > 10% (problemas sistêmicos)
- Tempo > 2min/arquivo (performance)

RELATÓRIOS GERAR:
- Estatísticas diárias de conversão
- Top issues de qualidade identificados
- Recomendações de melhoria
- Comparativo de métodos de conversão
```

## 🎨 Prompts para Personalização

### Configurações por Tipo de Documento
```
PERFIS DE CONVERSÃO POR TIPO:

DOCUMENTAÇÃO TÉCNICA:
- optimize: true (estrutura importante)
- validate: true (qualidade crítica)
- return_content: false (apenas arquivo)

RELATÓRIOS EXECUTIVOS:
- optimize: true (formatação profissional)
- validate: true (verificar completude)
- return_content: true (mostrar preview)

MATERIAL EDUCATIVO:
- optimize: true (clareza essencial)
- validate: true (detectar problemas estruturais)
- return_content: true (revisar conteúdo)

ARQUIVOS LEGAIS:
- optimize: false (preservar formatação original)
- validate: true (verificar integridade)
- return_content: false (segurança)
```

---

**Dica:** Adapte estes prompts conforme seu caso de uso específico. O agente é flexível e pode ser configurado para diferentes cenários através dos parâmetros JSON.