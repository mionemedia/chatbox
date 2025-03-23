import json
from pathlib import Path

# Default configuration
DEFAULT_CONFIG = {
    'theme': 'light',
    'window': {
        'width': 800,
        'height': 600,
        'min_width': 600,
        'min_height': 400
    },
    'ollama': {
        'host': 'http://localhost:11434',
        'parameters': {
            'temperature': 0.7,
            'top_p': 0.9,
            'top_k': 40
        }
    },
    'model': 'mistral',
    'save_path': 'saved_chats',
    'message_colors': {
        'user': '#1f6aa5',
        'assistant': '#2b9348',
        'system': '#757575'
    }
}

def load_settings():
    """Load settings from file or return defaults."""
    return DEFAULT_CONFIG.copy()

def save_settings(settings):
    """Save settings to file."""
    pass  # For testing, we don't need to actually save
