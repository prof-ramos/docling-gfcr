#!/usr/bin/env python3
"""
Interface Gráfica para Conversão de Documentos
Permite ao usuário selecionar arquivos e diretório de saída via interface visual.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
import sys
from pathlib import Path
from typing import Optional

# Adicionar o diretório do projeto ao path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.convert import convert_document, SUPPORTED_EXTENSIONS, DEFAULT_OUTPUT_DIR


class DocumentConverterGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Conversor de Documentos - Docling")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variáveis
        self.input_file = tk.StringVar()
        self.output_dir = tk.StringVar(value=DEFAULT_OUTPUT_DIR)
        self.progress = tk.StringVar(value="Pronto para conversão")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do usuário."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Conversor de Documentos", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Seção de arquivo de entrada
        ttk.Label(main_frame, text="Arquivo de entrada:", 
                 font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_file, 
                                    font=("Arial", 10), state="readonly")
        self.input_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(input_frame, text="Selecionar Arquivo", 
                  command=self.select_input_file).grid(row=0, column=1)
        
        # Extensões suportadas
        ext_text = "Extensões suportadas: " + ", ".join(sorted(SUPPORTED_EXTENSIONS))
        ttk.Label(main_frame, text=ext_text, font=("Arial", 8), 
                 foreground="gray").grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(0, 20))
        
        # Seção de diretório de saída
        ttk.Label(main_frame, text="Diretório de saída:", 
                 font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        output_frame.columnconfigure(0, weight=1)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_dir, 
                                     font=("Arial", 10))
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(output_frame, text="Selecionar Pasta", 
                  command=self.select_output_dir).grid(row=0, column=1)
        
        # Botão de conversão
        self.convert_button = ttk.Button(main_frame, text="Converter Documento", 
                                        command=self.start_conversion, 
                                        style="Accent.TButton")
        self.convert_button.grid(row=6, column=0, columnspan=3, pady=20)
        
        # Barra de progresso
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status
        self.status_label = ttk.Label(main_frame, textvariable=self.progress, 
                                     font=("Arial", 10))
        self.status_label.grid(row=8, column=0, columnspan=3, pady=(0, 10))
        
        # Área de resultado
        result_frame = ttk.LabelFrame(main_frame, text="Resultado", padding="10")
        result_frame.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=20)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        self.result_text = tk.Text(result_frame, height=8, wrap=tk.WORD, 
                                  font=("Arial", 9))
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configurar peso das linhas para expansão
        main_frame.rowconfigure(9, weight=1)
        
    def select_input_file(self):
        """Abre diálogo para seleção do arquivo de entrada."""
        # Criar filtros de arquivo baseados nas extensões suportadas
        filetypes = [
            ("Todos os suportados", " ".join(f"*{ext}" for ext in sorted(SUPPORTED_EXTENSIONS))),
            ("Documentos PDF", "*.pdf"),
            ("Documentos Word", "*.docx"),
            ("Planilhas Excel", "*.xlsx"),
            ("Apresentações PowerPoint", "*.pptx"),
            ("Páginas Web", "*.html *.xhtml"),
            ("Markdown", "*.md"),
            ("Arquivos CSV", "*.csv"),
            ("Imagens", "*.png *.jpeg *.jpg *.tiff *.tif *.bmp *.webp"),
            ("Arquivos XML/JSON", "*.xml *.json"),
            ("AsciiDoc", "*.adoc *.asciidoc"),
            ("Todos os arquivos", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Selecionar arquivo para conversão",
            filetypes=filetypes,
            initialdir=os.path.expanduser("~/Downloads")
        )
        
        if filename:
            self.input_file.set(filename)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Arquivo selecionado: {filename}\n")
            
    def select_output_dir(self):
        """Abre diálogo para seleção do diretório de saída."""
        directory = filedialog.askdirectory(
            title="Selecionar diretório de saída",
            initialdir=self.output_dir.get()
        )
        
        if directory:
            self.output_dir.set(directory)
            
    def start_conversion(self):
        """Inicia a conversão em thread separada."""
        if not self.input_file.get():
            messagebox.showerror("Erro", "Por favor, selecione um arquivo para conversão.")
            return
            
        if not self.output_dir.get():
            messagebox.showerror("Erro", "Por favor, selecione um diretório de saída.")
            return
            
        # Desabilitar botão e iniciar progresso
        self.convert_button.config(state="disabled")
        self.progress_bar.start(10)
        self.progress.set("Convertendo documento...")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Iniciando conversão...\n")
        
        # Executar conversão em thread separada
        thread = threading.Thread(target=self.perform_conversion)
        thread.daemon = True
        thread.start()
        
    def perform_conversion(self):
        """Executa a conversão do documento."""
        try:
            input_path = self.input_file.get()
            output_dir = self.output_dir.get()
            
            # Atualizar interface
            self.root.after(0, lambda: self.result_text.insert(tk.END, f"Arquivo: {input_path}\n"))
            self.root.after(0, lambda: self.result_text.insert(tk.END, f"Destino: {output_dir}\n\n"))
            
            # Executar conversão
            result = convert_document(input_path, output_dir, return_content=False)
            
            # Processar resultado
            self.root.after(0, lambda: self.handle_conversion_result(result))
            
        except Exception as e:
            error_msg = f"Erro durante a conversão: {str(e)}"
            self.root.after(0, lambda: self.handle_conversion_error(error_msg))
            
    def handle_conversion_result(self, result: dict):
        """Processa o resultado da conversão na thread principal."""
        self.progress_bar.stop()
        self.convert_button.config(state="normal")
        
        if result.get("success"):
            self.progress.set("Conversão concluída com sucesso!")
            
            method = result.get("method", "desconhecido")
            output_file = result.get("output_file", "")
            file_size = result.get("file_size_bytes", 0)
            
            self.result_text.insert(tk.END, "✅ CONVERSÃO CONCLUÍDA COM SUCESSO!\n\n")
            self.result_text.insert(tk.END, f"Método utilizado: {method}\n")
            self.result_text.insert(tk.END, f"Arquivo gerado: {output_file}\n")
            self.result_text.insert(tk.END, f"Tamanho do arquivo: {file_size:,} bytes\n\n")
            
            if output_file:
                # Botão para abrir pasta
                self.result_text.insert(tk.END, "Para visualizar o arquivo, abra a pasta de destino.\n")
                
            messagebox.showinfo("Sucesso", "Documento convertido com sucesso!")
            
        else:
            error = result.get("error", "Erro desconhecido")
            self.handle_conversion_error(error)
            
    def handle_conversion_error(self, error_msg: str):
        """Processa erros de conversão na thread principal."""
        self.progress_bar.stop()
        self.convert_button.config(state="normal")
        self.progress.set("Erro na conversão")
        
        self.result_text.insert(tk.END, f"❌ ERRO NA CONVERSÃO:\n\n{error_msg}\n")
        messagebox.showerror("Erro de Conversão", error_msg)


def main():
    """Função principal da aplicação GUI."""
    root = tk.Tk()
    
    # Configurar estilo
    style = ttk.Style()
    style.theme_use('clam')
    
    # Criar e executar aplicação
    app = DocumentConverterGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nAplicação encerrada pelo usuário.")
        

if __name__ == "__main__":
    main()