from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
import json
import os

class SettingsDialog(Popup):
    def __init__(self, settings=None, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.title = "Settings"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False
        
        self.default_settings = {
            "api_endpoint": "http://localhost:11434/api",
            "api_key": "",
            "model_name": "llama2",
            "use_local_model": True
        }
        
        self.settings = settings if settings else self.default_settings.copy()
        self.callback = callback
        self._init_ui()

    def _init_ui(self):
        # Main layout
        layout = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(10)
        )
        
        # Form layout
        form = GridLayout(
            cols=2,
            spacing=dp(10),
            row_default_height=dp(40),
            row_force_default=True,
            padding=dp(10)
        )
        
        # API Endpoint
        form.add_widget(Label(
            text="API Endpoint:",
            halign="right",
            valign="middle"
        ))
        self.api_endpoint = TextInput(
            text=self.settings.get("api_endpoint", ""),
            multiline=False,
            padding=dp(10)
        )
        form.add_widget(self.api_endpoint)
        
        # API Key
        form.add_widget(Label(
            text="API Key:",
            halign="right",
            valign="middle"
        ))
        self.api_key = TextInput(
            text=self.settings.get("api_key", ""),
            multiline=False,
            password=True,
            padding=dp(10)
        )
        form.add_widget(self.api_key)
        
        # Model Name
        form.add_widget(Label(
            text="Model Name:",
            halign="right",
            valign="middle"
        ))
        self.model_name = TextInput(
            text=self.settings.get("model_name", ""),
            multiline=False,
            padding=dp(10)
        )
        form.add_widget(self.model_name)
        
        # Use Local Model
        form.add_widget(Label(
            text="Use Local Model:",
            halign="right",
            valign="middle"
        ))
        local_box = BoxLayout(padding=dp(10))
        self.use_local = CheckBox(
            active=self.settings.get("use_local_model", True)
        )
        local_box.add_widget(self.use_local)
        form.add_widget(local_box)

        # Add form to layout
        layout.add_widget(form)
        
        # Buttons
        buttons = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
            spacing=dp(20),
            padding=dp(10)
        )
        
        save_btn = Button(
            text="Save",
            size_hint_x=0.5
        )
        save_btn.bind(on_press=self.save)
        
        cancel_btn = Button(
            text="Cancel",
            size_hint_x=0.5
        )
        cancel_btn.bind(on_press=self.dismiss)
        
        buttons.add_widget(save_btn)
        buttons.add_widget(cancel_btn)
        layout.add_widget(buttons)
        
        self.content = layout

    def save(self, instance):
        """Save the settings and close the dialog"""
        settings = {
            "api_endpoint": self.api_endpoint.text,
            "api_key": self.api_key.text,
            "model_name": self.model_name.text,
            "use_local_model": self.use_local.active
        }
        
        if self._validate_settings(settings):
            # Save settings
            self.settings = settings
            self._save_settings_to_file(settings)
            
            # Call the callback if provided
            if self.callback:
                self.callback(settings)
            
            # Close the dialog
            self.dismiss()

    def _validate_settings(self, settings):
        """Validate settings before saving"""
        if not settings["api_endpoint"]:
            self._show_error("API Endpoint is required")
            return False
        
        if not settings["model_name"]:
            self._show_error("Model Name is required")
            return False
        
        if not settings["use_local_model"] and not settings["api_key"]:
            self._show_error("API Key is required when not using local model")
            return False
        
        return True

    def _show_error(self, message):
        """Show error popup"""
        error_popup = Popup(
            title="Validation Error",
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200)
        )
        error_popup.open()

    def _save_settings_to_file(self, settings):
        """Save settings to a JSON file"""
        try:
            os.makedirs("settings", exist_ok=True)
            with open("settings/config.json", "w") as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

def load_settings():
    """Load settings from file or return defaults"""
    try:
        if os.path.exists("settings/config.json"):
            with open("settings/config.json", "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading settings: {e}")
    
    return {
        "api_endpoint": "http://localhost:11434/api",
        "api_key": "",
        "model_name": "llama2",
        "use_local_model": True
    }
