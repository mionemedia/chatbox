from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.config import Config
import asyncio
import os

# Configure the app
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
Config.set('graphics', 'minimum_width', '600')
Config.set('graphics', 'minimum_height', '400')

class ChatApp(App):
    def build(self):
        # Initialize settings
        self.settings = {
            "theme": "dark",
            "available_themes": ["light", "dark"]
        }
        self.available_models = ["llama2", "mistral", "codellama"]
        
        # Set window title
        self.title = "Chat Application"
        
        # Create the main layout
        self.main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Add menu bar
        self.menu_layout = GridLayout(cols=5, size_hint=(1, None), height=40)
        
        # File menu
        self.file_menu = Button(text='File', size_hint=(None, None), size=(80, 40))
        self.file_dropdown = DropDown()
        
        new_chat_btn = Button(text='New Chat', size_hint_y=None, height=40)
        new_chat_btn.bind(on_release=self.new_chat)
        self.file_dropdown.add_widget(new_chat_btn)
        
        save_chat_btn = Button(text='Save Chat', size_hint_y=None, height=40)
        save_chat_btn.bind(on_release=self.save_chat)
        self.file_dropdown.add_widget(save_chat_btn)
        
        exit_btn = Button(text='Exit', size_hint_y=None, height=40)
        exit_btn.bind(on_release=self.stop)
        self.file_dropdown.add_widget(exit_btn)
        
        self.file_menu.bind(on_release=self.file_dropdown.open)
        self.menu_layout.add_widget(self.file_menu)
        
        # Edit menu
        self.edit_menu = Button(text='Edit', size_hint=(None, None), size=(80, 40))
        self.edit_dropdown = DropDown()
        
        clear_chat_btn = Button(text='Clear Chat', size_hint_y=None, height=40)
        clear_chat_btn.bind(on_release=self.clear_chat)
        self.edit_dropdown.add_widget(clear_chat_btn)
        
        settings_btn = Button(text='Settings', size_hint_y=None, height=40)
        settings_btn.bind(on_release=self.toggle_settings)
        self.edit_dropdown.add_widget(settings_btn)
        
        self.edit_menu.bind(on_release=self.edit_dropdown.open)
        self.menu_layout.add_widget(self.edit_menu)
        
        # Theme menu
        self.theme_menu = Button(text='Theme', size_hint=(None, None), size=(80, 40))
        self.theme_dropdown = DropDown()
        
        for theme_name in self.settings.get("available_themes", ["light", "dark"]):
            theme_display_name = theme_name.capitalize()
            theme_btn = Button(text=theme_display_name, size_hint_y=None, height=40)
            theme_btn.bind(on_release=lambda btn, tn=theme_name: self.change_theme(tn))
            self.theme_dropdown.add_widget(theme_btn)
        
        self.theme_menu.bind(on_release=self.theme_dropdown.open)
        self.menu_layout.add_widget(self.theme_menu)
        
        self.main_layout.add_widget(self.menu_layout)
        
        # Chat display area
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.chat_display = TextInput(
            text='',
            multiline=True,
            readonly=True,
            size_hint=(1, None),
            height=Window.height
        )
        self.chat_display.bind(minimum_height=self.chat_display.setter('height'))
        self.scroll_view.add_widget(self.chat_display)
        self.main_layout.add_widget(self.scroll_view)
        
        # Input area
        self.input_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=50,
            spacing=10
        )
        
        self.message_input = TextInput(
            hint_text='Type your message here...',
            multiline=False,
            size_hint=(0.85, 1)
        )
        self.message_input.bind(on_text_validate=self.send_message)
        self.input_layout.add_widget(self.message_input)
        
        self.send_button = Button(text='Send', size_hint=(0.15, 1))
        self.send_button.bind(on_release=self.send_message)
        self.input_layout.add_widget(self.send_button)
        
        self.main_layout.add_widget(self.input_layout)
        
        # Display welcome message
        Clock.schedule_once(
            lambda dt: self.receive_message("Welcome to the Chat Application! Type a message to begin."),
            0.1
        )
        
        return self.main_layout

    async def connect_to_ollama(self):
        """Connect to the Ollama API server"""
        return True

    def update_status(self, status_text, status_type="info"):
        """Update the status bar with new text and appropriate styling."""
        print(f"Status: {status_text} [{status_type}]")

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        current_theme = self.settings["theme"]
        new_theme = "light" if current_theme == "dark" else "dark"
        self.change_theme(new_theme)

    def clear_chat(self, instance=None):
        """Clear the chat display"""
        self.chat_display.text = ''
        print("Clear chat clicked")

    def save_chat(self, instance=None):
        """Save chat content to a file"""
        content = self.chat_display.text
        try:
            # Open file dialog popup
            self.show_save_dialog(content)
        except Exception as e:
            self.show_popup("Save Failed", f"Error: {str(e)}")

    def show_save_dialog(self, content):
        """Show a file save dialog"""
        layout = BoxLayout(orientation='vertical')
        
        # Add a text input for filename
        filename_input = TextInput(
            text='chat_history.txt',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(Label(text='Enter filename:'))
        layout.add_widget(filename_input)
        
        # Add buttons
        buttons = BoxLayout(size_hint_y=None, height=40)
        
        save_btn = Button(text='Save')
        cancel_btn = Button(text='Cancel')
        
        def save(instance):
            try:
                with open(filename_input.text, 'w') as f:
                    f.write(content)
                self.show_popup("Success", "Chat saved successfully!")
                popup.dismiss()
            except Exception as e:
                self.show_popup("Error", f"Failed to save: {str(e)}")
        
        save_btn.bind(on_release=save)
        cancel_btn.bind(on_release=lambda x: popup.dismiss())
        
        buttons.add_widget(save_btn)
        buttons.add_widget(cancel_btn)
        layout.add_widget(buttons)
        
        popup = Popup(
            title='Save Chat',
            content=layout,
            size_hint=(None, None),
            size=(400, 200)
        )
        popup.open()

    def send_message(self, instance):
        """Send a message"""
        message = self.message_input.text
        if message:
            self.receive_message(f"You: {message}")
            self.message_input.text = ''

    def receive_message(self, message):
        """Display a received message"""
        self.chat_display.text += f"{message}\n"
        # Scroll to the bottom
        self.chat_display.cursor = (0, len(self.chat_display.text))

    def new_chat(self, instance=None):
        """Start a new chat"""
        self.clear_chat()
        self.receive_message("Welcome to the Chat Application! Type a message to begin.")

    def toggle_settings(self, instance=None):
        """Toggle settings panel"""
        self.show_popup("Settings", "Settings panel would appear here.")

    def change_theme(self, theme_name):
        """Change the theme"""
        self.settings["theme"] = theme_name
        # Apply theme changes (simplified for demo)
        bg_color = (0.1, 0.1, 0.1, 1) if theme_name == "dark" else (0.9, 0.9, 0.9, 1)
        text_color = (0.9, 0.9, 0.9, 1) if theme_name == "dark" else (0.1, 0.1, 0.1, 1)
        self.chat_display.background_color = bg_color
        self.chat_display.foreground_color = text_color
        self.show_popup("Theme Changed", f"Theme changed to {theme_name}")

    def show_popup(self, title, content):
        """Show a popup with the given title and content"""
        popup = Popup(
            title=title,
            content=Label(text=content),
            size_hint=(None, None),
            size=(400, 200)
        )
        popup.open()

if __name__ == "__main__":
    ChatApp().run()
