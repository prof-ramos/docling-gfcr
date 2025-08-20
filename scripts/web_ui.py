#!/usr/bin/env python3
"""
Interface Web para Conversão de Documentos
Interface simples e moderna usando Streamlit para seleção de arquivos e conversão.
"""
from __future__ import annotations

import streamlit as st
import tempfile
import os
import sys
from pathlib import Path
from typing import Optional

# Adicionar o diretório do projeto ao path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.convert import convert_document, SUPPORTED_EXTENSIONS, DEFAULT_OUTPUT_DIR


def main():
    """Interface principal da aplicação web."""
    
    # Configurar a página
    st.set_page_config(
        page_title="Conversor de Documentos - Docling",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS customizado
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        color: #721c24;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Cabeçalho principal
    st.markdown("""
    <div class="main-header">
        <h1>🔄 Conversor de Documentos</h1>
        <p>Interface Web - Powered by Docling</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar com informações
    with st.sidebar:
        st.header("ℹ️ Informações")
        
        st.subheader("📁 Extensões Suportadas")
        extensions_text = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        st.text(extensions_text)
        
        st.subheader("🔧 Como Usar")
        st.markdown("""
        1. **Upload**: Envie seu arquivo
        2. **Configurar**: Escolha opções de saída  
        3. **Converter**: Clique no botão de conversão
        4. **Download**: Baixe o arquivo convertido
        """)
        
        st.subheader("📊 Status")
        if "conversion_status" in st.session_state:
            st.write(f"Status: {st.session_state.conversion_status}")
    
    # Layout principal em colunas
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📤 Upload do Arquivo")
        
        # Upload de arquivo
        uploaded_file = st.file_uploader(
            "Selecione o arquivo para conversão",
            type=[ext.lstrip('.') for ext in SUPPORTED_EXTENSIONS],
            help="Arraste e solte o arquivo ou clique para selecionar"
        )
        
        if uploaded_file is not None:
            # Exibir informações do arquivo
            file_details = {
                "Nome": uploaded_file.name,
                "Tamanho": f"{uploaded_file.size:,} bytes",
                "Tipo": uploaded_file.type or "Desconhecido"
            }
            
            st.subheader("📋 Detalhes do Arquivo")
            for key, value in file_details.items():
                st.text(f"{key}: {value}")
    
    with col2:
        st.header("⚙️ Configurações")
        
        # Configurações de saída
        output_format = st.selectbox(
            "Formato de saída",
            ["Markdown (.md)", "Texto (.txt)"],
            index=0
        )
        
        return_content = st.checkbox(
            "Mostrar conteúdo na tela",
            value=True,
            help="Exibir o conteúdo convertido diretamente na interface"
        )
        
        custom_output = st.checkbox(
            "Usar diretório personalizado",
            value=False
        )
        
        if custom_output:
            output_dir = st.text_input(
                "Diretório de saída",
                value=str(Path.home() / "Downloads"),
                help="Caminho completo para o diretório onde salvar o arquivo"
            )
        else:
            output_dir = DEFAULT_OUTPUT_DIR
            st.text(f"Padrão: {output_dir}")
    
    # Botão de conversão
    st.divider()
    
    if uploaded_file is not None:
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        
        with col_btn2:
            if st.button("🔄 Converter Documento", type="primary", use_container_width=True):
                convert_document_ui(uploaded_file, output_dir, return_content, output_format)
    else:
        st.info("👆 Por favor, faça upload de um arquivo para habilitar a conversão")
    
    # Área de resultados
    if "conversion_result" in st.session_state:
        show_conversion_result()


def convert_document_ui(uploaded_file, output_dir: str, return_content: bool, output_format: str):
    """Executa a conversão do documento na interface."""
    
    try:
        # Mostrar progresso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Preparando conversão...")
        progress_bar.progress(25)
        
        # Salvar arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        status_text.text("Executando conversão...")
        progress_bar.progress(50)
        
        # Executar conversão
        result = convert_document(
            input_path=tmp_path,
            output_dir=output_dir,
            return_content=return_content
        )
        
        progress_bar.progress(75)
        
        # Processar resultado
        if result.get("success"):
            status_text.text("Conversão concluída!")
            progress_bar.progress(100)
            
            # Salvar resultado no estado da sessão
            st.session_state.conversion_result = result
            st.session_state.conversion_status = "Sucesso"
            
            # Limpar arquivos temporários
            try:
                os.unlink(tmp_path)
            except:
                pass
                
            st.rerun()
            
        else:
            error_msg = result.get("error", "Erro desconhecido")
            st.session_state.conversion_result = result
            st.session_state.conversion_status = "Erro"
            
            # Limpar arquivos temporários
            try:
                os.unlink(tmp_path)
            except:
                pass
                
            st.rerun()
            
    except Exception as e:
        st.session_state.conversion_result = {
            "success": False,
            "error": str(e)
        }
        st.session_state.conversion_status = "Erro"
        st.rerun()


def show_conversion_result():
    """Exibe os resultados da conversão."""
    
    result = st.session_state.conversion_result
    
    st.divider()
    st.header("📊 Resultado da Conversão")
    
    if result.get("success"):
        st.markdown("""
        <div class="success-box">
            <h3>✅ Conversão Realizada com Sucesso!</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Detalhes do resultado
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Detalhes")
            details = {
                "Método": result.get("method", "Desconhecido"),
                "Arquivo gerado": Path(result.get("output_file", "")).name,
                "Tamanho": f"{result.get('file_size_bytes', 0):,} bytes"
            }
            
            for key, value in details.items():
                st.text(f"{key}: {value}")
        
        with col2:
            st.subheader("📁 Localização")
            output_file = result.get("output_file", "")
            if output_file:
                st.text(f"Caminho completo:")
                st.code(output_file, language="text")
                
                # Botão para copiar caminho
                if st.button("📋 Copiar Caminho", key="copy_path"):
                    st.write("Caminho copiado para área de transferência!")
        
        # Mostrar conteúdo se solicitado
        if "content" in result and result["content"]:
            st.subheader("📄 Conteúdo Convertido")
            
            # Limitar exibição para performance
            content = result["content"]
            if len(content) > 10000:
                st.warning("⚠️ Conteúdo muito grande. Mostrando apenas os primeiros 10.000 caracteres...")
                content = content[:10000] + "\n\n[... conteúdo truncado ...]"
            
            st.text_area(
                "Resultado da conversão:",
                content,
                height=300,
                key="converted_content"
            )
            
            # Botão de download
            st.download_button(
                label="💾 Download do Conteúdo",
                data=result["content"],
                file_name=Path(output_file).name if output_file else "converted.md",
                mime="text/markdown"
            )
    
    else:
        error_msg = result.get("error", "Erro desconhecido")
        st.markdown(f"""
        <div class="error-box">
            <h3>❌ Erro na Conversão</h3>
            <p><strong>Detalhes:</strong> {error_msg}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sugestões para resolução
        st.subheader("💡 Possíveis Soluções")
        st.markdown("""
        - Verifique se o arquivo não está corrompido
        - Confirme se a extensão é suportada
        - Tente um arquivo menor
        - Verifique as permissões do diretório de saída
        """)
    
    # Botão para nova conversão
    if st.button("🔄 Nova Conversão", use_container_width=True):
        for key in ["conversion_result", "conversion_status"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()


if __name__ == "__main__":
    main()