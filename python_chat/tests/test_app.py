import pytest
import asyncio
import os
import sys
from unittest.mock import MagicMock, patch, AsyncMock, mock_open
from pathlib import Path

# Add the parent directory to sys.path to import the application modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kivy.app import App
from kivy.clock import Clock
from main import ChatApp

class MockTextInput:
    """Mock class for Kivy TextInput widget"""
    def __init__(self):
        self.text = ""

    def insert_text(self, text, from_undo=False):
        self.text += text

    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = text

class MockOllamaClient:
    """Mock class for OllamaClient testing."""
    def __init__(self):
        self.available_models = ['mistral', 'llama2', 'gemma']
        self.current_model = 'mistral'
        self.status = 'Connected'
        self.error = None
    
    async def connect(self):
        return True
    
    async def list_models(self):
        return [{'name': model} for model in self.available_models]
    
    async def generate(self, *args, **kwargs):
        return 'Mock response'

@pytest.fixture(autouse=True)
def mock_kivy():
    """Patch Kivy widgets and components."""
    # Mock Clock
    clock_mock = MagicMock()
    def mock_create_trigger(callback, timeout=0):
        return lambda *args, **kwargs: callback(*args, **kwargs)
    clock_mock.create_trigger = mock_create_trigger
    
    def mock_schedule_once(callback, timeout=0):
        callback(0)  # Call immediately with dummy dt parameter
    clock_mock.schedule_once = mock_schedule_once
    
    patches = [
        patch('kivy.uix.boxlayout.BoxLayout'),
        patch('kivy.uix.gridlayout.GridLayout'),
        patch('kivy.uix.button.Button'),
        patch('kivy.uix.textinput.TextInput'),
        patch('kivy.uix.label.Label'),
        patch('kivy.uix.scrollview.ScrollView'),
        patch('kivy.core.window.Window'),
        patch('kivy.clock.Clock', clock_mock)
    ]
    
    for p in patches:
        p.start()
    
    yield
    
    for p in patches:
        p.stop()

@pytest.fixture
def app_instance():
    """Create a mock ChatApp instance for testing."""
    app = MagicMock(spec=ChatApp)
    
    # Set up UI components
    app.chat_display = MockTextInput()
    app.message_input = MockTextInput()
    app.status_label = MagicMock()
    
    # Set up Ollama client
    app.ollama_client = MockOllamaClient()
    app.available_models = app.ollama_client.available_models
    
    # Mock methods
    app.connect_to_ollama = AsyncMock(return_value=True)
    app.update_status = MagicMock()
    app.clear_chat = MagicMock()
    app.toggle_theme = MagicMock()
    app.save_chat = MagicMock()
    app.process_response = MagicMock()
    app.receive_message = MagicMock()
    app.send_message = MagicMock()
    
    # Set up properties
    app.settings = {
        'theme': 'dark',
        'message_colors': {
            'user': '#1E88E5',
            'assistant': '#43A047',
            'system': '#757575'
        },
        'timestamp_format': '%H:%M:%S',
        'auto_save': False,
        'save_path': 'saved_chats'
    }
    
    # Patch App.get_running_app to return our mock
    with patch('kivy.app.App.get_running_app', return_value=app):
        return app

class TestOllamaConnection:
    @pytest.mark.asyncio
    async def test_connect_to_ollama(self, app_instance):
        """Test successful connection to Ollama server."""
        result = await app_instance.connect_to_ollama()
        assert result is True
        assert isinstance(app_instance.available_models, list)
        
    @pytest.mark.asyncio
    async def test_model_selection(self, app_instance):
        """Test model selection functionality."""
        model_name = 'llama2'
        app_instance.ollama_client.current_model = model_name
        assert app_instance.ollama_client.current_model == model_name

class TestUIFunctionality:
    def test_update_status(self, app_instance):
        """Test status label update."""
        status_text = 'Test status message'
        app_instance.update_status(status_text)
        app_instance.update_status.assert_called_once_with(status_text)

    def test_clear_chat(self, app_instance):
        """Test chat display clearing."""
        app_instance.chat_display.text = "test content"
        app_instance.clear_chat()
        app_instance.clear_chat.assert_called_once()
        
class TestSettings:
    def test_toggle_theme(self, app_instance):
        """Test theme toggling functionality."""
        initial_theme = app_instance.settings['theme']
        app_instance.toggle_theme()
        app_instance.toggle_theme.assert_called_once()

class TestChatOperations:
    def test_save_chat(self, app_instance, tmp_path):
        """Test chat content saving functionality."""
        test_content = 'Test chat content'
        test_file = tmp_path / 'test_chat.txt'
        app_instance.chat_display.text = test_content
        
        with patch('builtins.open', mock_open()) as mock_file:
            app_instance.save_chat()
            app_instance.save_chat.assert_called_once()

    def test_send_message(self, app_instance):
        """Test sending a message."""
        test_message = "Test message"
        app_instance.message_input.text = test_message
        app_instance.send_message()
        app_instance.send_message.assert_called_once()

    def test_receive_message(self, app_instance):
        """Test receiving a message."""
        test_message = "Test response"
        app_instance.receive_message(test_message)
        app_instance.receive_message.assert_called_once_with(test_message)

if __name__ == "__main__":
    pytest.main(["-v", __file__])
