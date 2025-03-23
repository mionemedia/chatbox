from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from settings_dialog import SettingsDialog, load_settings

class TestSettingsApp(App):
    """Test application demonstrating the settings dialog usage"""
    
    def build(self):
        # Set window properties
        self.title = "Settings Dialog Demo"
        Window.size = (600, 800)
        
        # Load current settings
        self.settings = load_settings()
        
        # Create main layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Add header
        layout.add_widget(Label(
            text="Settings Dialog Demo",
            font_size=24,
            size_hint_y=None,
            height=50
        ))
        
        # Button to open settings
        btn = Button(
            text="Open Settings",
            size_hint_y=None,
            height=50
        )
        btn.bind(on_press=self.show_settings)
        layout.add_widget(btn)
        
        # Settings display area
        self.settings_label = Label(
            text="Click 'Open Settings' to configure",
            size_hint_y=None,
            height=400,
            valign='top'
        )
        layout.add_widget(self.settings_label)
        
        return layout
    
    def show_settings(self, instance):
        """Open the settings dialog"""
        dialog = SettingsDialog(
            settings=self.settings,
            callback=self.on_settings_saved
        )
        dialog.open()
    
    def on_settings_saved(self, new_settings):
        """Handle saved settings"""
        self.settings = new_settings
        
        # Update display
        settings_text = "Current Settings:\n\n"
        for key, value in self.settings.items():
            # Mask API key
            if key == "api_key" and value:
                display_value = "*" * len(value)
            else:
                display_value = value
            settings_text += f"{key}: {display_value}\n"
        
        self.settings_label.text = settings_text

if __name__ == "__main__":
    TestSettingsApp().run()
