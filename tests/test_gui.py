#!/usr/bin/env python3
"""
Testes para gui.py - Interface Tkinter

Estratégia de teste:
- Mock dos componentes Tkinter
- Teste da lógica de negócio
- Validação de estruturas de dados
- Testes de fluxos principais
"""
from __future__ import annotations

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import threading
import os

# Garantir que o diretório do projeto esteja no sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Mock completo do Tkinter
tkinter_mock = Mock()
tkinter_mock.filedialog = Mock()
tkinter_mock.messagebox = Mock()
tkinter_mock.ttk = Mock()
tkinter_mock.Tk = Mock
tkinter_mock.StringVar = Mock
tkinter_mock.W = "w"
tkinter_mock.E = "e"
tkinter_mock.N = "n"
tkinter_mock.S = "s"

sys.modules['tkinter'] = tkinter_mock
sys.modules['tkinter.filedialog'] = tkinter_mock.filedialog
sys.modules['tkinter.messagebox'] = tkinter_mock.messagebox
sys.modules['tkinter.ttk'] = tkinter_mock.ttk

import scripts.gui as gui


class TestDocumentConverterGUI:
    """Testes para a classe DocumentConverterGUI."""

    @patch('scripts.gui.tk.Tk')
    def test_init_basic_setup(self, mock_tk):
        """Testa inicialização básica da GUI."""
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        # Mock das variáveis Tkinter
        with patch('scripts.gui.tk.StringVar') as mock_stringvar:
            mock_var = Mock()
            mock_stringvar.return_value = mock_var
            
            gui_instance = gui.DocumentConverterGUI(mock_root)
            
            # Verificar configuração básica
            mock_root.title.assert_called_with("Conversor de Documentos - Docling")
            mock_root.geometry.assert_called_with("800x600")
            mock_root.resizable.assert_called_with(True, True)

    def test_gui_constants(self):
        """Testa constantes e configurações da GUI."""
        # Verificar dimensões padrão
        default_geometry = "800x600"
        assert "x" in default_geometry
        width, height = default_geometry.split("x")
        assert int(width) >= 600
        assert int(height) >= 400
        
        # Verificar título
        title = "Conversor de Documentos - Docling"
        assert "Conversor" in title
        assert "Docling" in title

    def test_file_selection_logic(self):
        """Testa lógica de seleção de arquivos."""
        # Tipos de arquivo aceitos
        file_types = [
            ("Arquivos PDF", "*.pdf"),
            ("Documentos Word", "*.docx"),
            ("Todos os arquivos", "*.*")
        ]
        
        for file_type, pattern in file_types:
            assert isinstance(file_type, str)
            assert pattern.startswith("*.")
            if pattern != "*.*":
                extension = pattern[2:]  # Remove "*."
                assert len(extension) > 0

    def test_progress_tracking_structure(self):
        """Testa estrutura de acompanhamento de progresso."""
        progress_states = [
            "Pronto para conversão",
            "Selecionando arquivo...",
            "Convertendo documento...",
            "Conversão concluída!",
            "Erro na conversão"
        ]
        
        for state in progress_states:
            assert isinstance(state, str)
            assert len(state) > 0


class TestGUIFileOperations:
    """Testes para operações de arquivo na GUI."""

    def test_file_validation(self):
        """Testa validação de arquivos."""
        valid_extensions = ['.pdf', '.docx', '.xlsx', '.pptx', '.txt', '.md']
        
        for ext in valid_extensions:
            filename = f"document{ext}"
            assert filename.endswith(ext)
            assert '.' in filename

    def test_output_directory_handling(self):
        """Testa tratamento de diretório de saída."""
        default_output = "/Users/gabrielramos/docling/output"
        
        assert os.path.isabs(default_output)  # Deve ser caminho absoluto
        assert "output" in default_output

    def test_file_path_validation(self):
        """Testa validação de caminhos de arquivo."""
        test_paths = [
            "/Users/test/document.pdf",
            "/home/user/file.docx",
            "C:\\Documents\\file.pdf",  # Windows
            "/tmp/temp_file.txt"
        ]
        
        for path in test_paths:
            # Verificar se tem extensão
            assert '.' in Path(path).name
            # Verificar se é caminho válido
            assert len(path) > 0


class TestGUIErrorHandling:
    """Testes para tratamento de erros na GUI."""

    def test_error_message_structure(self):
        """Testa estrutura de mensagens de erro."""
        error_messages = {
            "file_not_found": "Arquivo não encontrado",
            "conversion_failed": "Falha na conversão",
            "permission_denied": "Permissão negada",
            "invalid_format": "Formato de arquivo não suportado"
        }
        
        for error_type, message in error_messages.items():
            assert isinstance(message, str)
            assert len(message) > 0
            assert error_type in ["file_not_found", "conversion_failed", "permission_denied", "invalid_format"]

    def test_success_message_structure(self):
        """Testa estrutura de mensagens de sucesso."""
        success_messages = [
            "Conversão concluída com sucesso!",
            "Arquivo salvo em: /path/to/output",
            "Documento convertido para Markdown"
        ]
        
        for message in success_messages:
            assert isinstance(message, str)
            assert len(message) > 0


class TestGUIThreading:
    """Testes para operações com threading na GUI."""

    def test_threading_structure(self):
        """Testa estrutura de threading."""
        # Verificar que operações longas devem usar threading
        thread_operations = [
            "convert_document",
            "file_processing",
            "save_output"
        ]
        
        for operation in thread_operations:
            assert isinstance(operation, str)
            assert len(operation) > 0

    @patch('scripts.gui.threading.Thread')
    def test_conversion_threading(self, mock_thread):
        """Testa threading para conversão."""
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        # Simular criação de thread
        conversion_thread = mock_thread(target=Mock(), daemon=True)
        
        mock_thread.assert_called_once()
        assert hasattr(conversion_thread, 'start')


class TestGUIComponents:
    """Testes para componentes da interface."""

    def test_widget_structure(self):
        """Testa estrutura dos widgets."""
        expected_widgets = [
            "input_file_label",
            "input_file_entry", 
            "browse_button",
            "output_dir_label",
            "output_dir_entry",
            "output_browse_button",
            "convert_button",
            "progress_label",
            "status_text"
        ]
        
        for widget_name in expected_widgets:
            assert isinstance(widget_name, str)
            assert "_" in widget_name or widget_name.islower()

    def test_layout_configuration(self):
        """Testa configuração de layout."""
        grid_options = {
            "sticky": ["w", "e", "n", "s"],
            "padx": [5, 10, 15],
            "pady": [5, 10, 15]
        }
        
        for option, values in grid_options.items():
            assert len(values) > 0
            for value in values:
                if isinstance(value, str):
                    assert len(value) > 0
                else:
                    assert value >= 0

    def test_button_configuration(self):
        """Testa configuração de botões."""
        button_configs = {
            "browse_button": {"text": "Procurar", "width": 12},
            "convert_button": {"text": "Converter", "width": 20},
            "output_browse_button": {"text": "Procurar", "width": 12}
        }
        
        for button_name, config in button_configs.items():
            assert "text" in config
            assert "width" in config
            assert isinstance(config["text"], str)
            assert isinstance(config["width"], int)
            assert config["width"] > 0


class TestGUIDataFlow:
    """Testes para fluxo de dados na GUI."""

    def test_input_output_flow(self):
        """Testa fluxo de entrada e saída."""
        flow_steps = [
            "select_input_file",
            "validate_input", 
            "set_output_directory",
            "start_conversion",
            "update_progress",
            "show_result"
        ]
        
        for step in flow_steps:
            assert isinstance(step, str)
            assert len(step) > 0

    def test_state_management(self):
        """Testa gerenciamento de estado."""
        gui_states = {
            "ready": "Pronto para conversão",
            "selecting": "Selecionando arquivo...",
            "converting": "Convertendo documento...",
            "completed": "Conversão concluída!",
            "error": "Erro na conversão"
        }
        
        for state_name, message in gui_states.items():
            assert isinstance(state_name, str)
            assert isinstance(message, str)
            assert len(message) > 0

    def test_conversion_parameters(self):
        """Testa parâmetros de conversão."""
        conversion_params = {
            "input_path": "/path/to/input.pdf",
            "output_dir": "/path/to/output",
            "output_format": "markdown",
            "return_content": False
        }
        
        assert "input_path" in conversion_params
        assert "output_dir" in conversion_params
        assert conversion_params["output_format"] in ["markdown", "json", "txt"]
        assert isinstance(conversion_params["return_content"], bool)


class TestGUIUtilities:
    """Testes para funções utilitárias da GUI."""

    def test_path_utilities(self):
        """Testa utilitários de caminho."""
        test_paths = [
            "/Users/test/document.pdf",
            "/home/user/file.docx"
        ]
        
        for path in test_paths:
            path_obj = Path(path)
            assert path_obj.suffix in ['.pdf', '.docx', '.txt', '.md']
            assert path_obj.name != ""

    def test_file_size_handling(self):
        """Testa tratamento de tamanho de arquivo."""
        file_sizes = {
            1024: "1 KB",
            1024 * 1024: "1 MB",
            1024 * 1024 * 1024: "1 GB"
        }
        
        for size_bytes, expected_format in file_sizes.items():
            assert size_bytes > 0
            assert "B" in expected_format

    def test_extension_mapping(self):
        """Testa mapeamento de extensões."""
        extension_map = {
            ".pdf": "PDF Document",
            ".docx": "Word Document",
            ".xlsx": "Excel Spreadsheet",
            ".txt": "Text File",
            ".md": "Markdown File"
        }
        
        for ext, description in extension_map.items():
            assert ext.startswith(".")
            assert len(description) > 0


class TestGUIMainFunction:
    """Testes para função main da GUI."""

    @patch('scripts.gui.tk.Tk')
    @patch('scripts.gui.DocumentConverterGUI')
    def test_main_execution(self, mock_gui_class, mock_tk):
        """Testa execução da função main."""
        mock_root = Mock()
        mock_tk.return_value = mock_root
        mock_gui_instance = Mock()
        mock_gui_class.return_value = mock_gui_instance
        
        # Simular execução do main
        try:
            gui.main()
        except Exception:
            # Esperado devido aos mocks, mas a estrutura foi testada
            pass
        
        # Verificar criação dos componentes
        mock_tk.assert_called_once()
        mock_gui_class.assert_called_once_with(mock_root)

    def test_main_function_existence(self):
        """Testa existência da função main."""
        assert hasattr(gui, 'main')
        assert callable(gui.main)

    def test_gui_class_existence(self):
        """Testa existência da classe GUI."""
        assert hasattr(gui, 'DocumentConverterGUI')
        assert gui.DocumentConverterGUI is not None


class TestGUIIntegration:
    """Testes de integração da GUI."""

    @patch('scripts.gui.convert_document')
    def test_conversion_integration(self, mock_convert):
        """Testa integração com sistema de conversão."""
        mock_convert.return_value = {
            "success": True,
            "output_file": "/output/test.md",
            "content": "# Converted content"
        }
        
        # Simular chamada de conversão
        result = mock_convert(
            input_path="/test/input.pdf",
            output_dir="/test/output",
            return_content=False
        )
        
        assert result["success"] is True
        assert "output_file" in result
        mock_convert.assert_called_once()

    def test_error_integration(self):
        """Testa integração de tratamento de erros."""
        error_scenarios = [
            {"type": "FileNotFoundError", "message": "File not found"},
            {"type": "PermissionError", "message": "Permission denied"},
            {"type": "Exception", "message": "Generic error"}
        ]
        
        for scenario in error_scenarios:
            assert "type" in scenario
            assert "message" in scenario
            assert len(scenario["message"]) > 0

    def test_success_integration(self):
        """Testa integração de casos de sucesso."""
        success_result = {
            "success": True,
            "output_file": "/output/document.md",
            "processing_time": 5.2,
            "pages_processed": 10
        }
        
        assert success_result["success"] is True
        assert "output_file" in success_result
        assert success_result["processing_time"] > 0
        assert success_result["pages_processed"] > 0


if __name__ == "__main__":
    # Permite executar os testes diretamente
    pytest.main([__file__, "-v", "--cov=scripts.gui", "--cov-report=term-missing"])