"""
Base Page class for all installer wizard pages
"""
import tkinter as tk
from tkinter import ttk
import os
import tomllib

class BasePage:
    """Base class for all installer wizard pages."""
    
    def __init__(self, container, app):
        """Initialize the base page.
        
        Args:
            container: The parent container (frame)
            app: The main application instance for accessing shared state
        """
        self.container = container
        self.app = app
        self.frame = ttk.Frame(container)
        
        # Common elements
        self.header_frame = ttk.Frame(self.frame)
        self.header_frame.pack(fill="x", padx=10, pady=(20, 10))
        
        self.title_label = ttk.Label(self.header_frame, style="Title.TLabel")
        self.title_label.pack(anchor="w")
        
        self.subtitle_label = ttk.Label(self.header_frame, style="Heading.TLabel")
        self.subtitle_label.pack(anchor="w", pady=(5, 0))
        
        # Content area
        self.content_frame = ttk.Frame(self.frame)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Button area at bottom
        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.pack(fill="x", side="bottom", padx=10, pady=10)
        
        self.back_button = ttk.Button(self.button_frame, text="Back", command=self.on_back)
        self.back_button.pack(side="left", padx=5, pady=5)
        
        self.next_button = ttk.Button(self.button_frame, text="Next", command=self.on_next)
        self.next_button.pack(side="right", padx=5, pady=5)
        
        # Create page-specific widgets
        self.create_widgets()
    
    def create_widgets(self):
        """Create page-specific widgets.
        
        Override in subclasses to add page-specific content.
        """
        pass
    
    def on_enter(self):
        """Called when the page is shown.
        
        Override in subclasses for page-specific initialization.
        """
        pass
    
    def on_leave(self):
        """Called when leaving the page.
        
        Override in subclasses for page-specific cleanup.
        """
        pass
    
    def on_next(self):
        """Handle next button click.
        
        Validates and saves data, then advances to the next page.
        """
        if self.validate():
            self.save_data()
            self.on_leave()
            self.app.next_page()
    
    def on_back(self):
        """Handle back button click."""
        self.on_leave()
        self.app.prev_page()
    
    def validate(self):
        """Validate the page data before proceeding.
        
        Returns:
            bool: True if validation passes, False otherwise
        """
        return True
    
    def save_data(self):
        """Save the data from this page to the app's user_config.
        
        Override in subclasses to save page-specific data.
        """
        pass
    
    def show(self):
        """Show this page."""
        self.frame.pack(fill="both", expand=True)
        self.on_enter()
    
    def hide(self):
        """Hide this page."""
        self.frame.pack_forget()
    
    def set_title(self, title, subtitle=""):
        """Set the page title and subtitle.
        
        Args:
            title: The main title text
            subtitle: The subtitle text
        """
        self.title_label.config(text=title)
        self.subtitle_label.config(text=subtitle)
        
    def set_next_button_text(self, text):
        """Change the text of the next button.
        
        Args:
            text: The new button text
        """
        self.next_button.config(text=text)
        
    def set_back_button_state(self, enabled=True):
        """Enable or disable the back button.
        
        Args:
            enabled: True to enable, False to disable
        """
        self.back_button.config(state="normal" if enabled else "disabled")
        
    def set_next_button_state(self, enabled=True):
        """Enable or disable the next button.
        
        Args:
            enabled: True to enable, False to disable
        """
        self.next_button.config(state="normal" if enabled else "disabled")
        
    def update_installed_config(self, key, value):
        """Update a configuration value in the installed config file.
        
        Args:
            key: Configuration key path (e.g., "display.monitor_index")
            value: New value to set
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        if not self.app.user_config.get("install_path"):
            return False
            
        install_path = self.app.user_config["install_path"]
        config_dir = os.path.join(install_path, "config")
        
        # Determine which config file to update based on the key prefix
        config_file = None
        if key.startswith("display.") or key.startswith("dynamic_marquee."):
            config_file = os.path.join(config_dir, "display_config.toml")
        elif key.startswith("default."):
            config_file = os.path.join(config_dir, "default_config.toml")
        elif key.startswith("keys."):
            config_file = os.path.join(config_dir, "key_listener.toml")
        elif key.startswith("process_names."):
            config_file = os.path.join(config_dir, "processes_to_kill.toml")
        elif key.startswith("mame."):
            config_file = os.path.join(config_dir, "mame_config.toml")
        elif key.startswith("screenshot.") or key.startswith("icloud."):
            config_file = os.path.join(config_dir, "screenshot_config.toml")
        elif key.startswith("lights.") or key.startswith("streaming.") or key.startswith("vpn.") or key.startswith("volume_control."):
            config_file = os.path.join(config_dir, "utility_config.toml")
        elif key.startswith("pegasus."):
            config_file = os.path.join(config_dir, "pegasus_binaries.toml")
        elif key.startswith("games."):
            config_file = os.path.join(config_dir, "installed_games.toml")
        
        if not config_file or not os.path.exists(config_file):
            return False
        
        try:
            # Read existing config
            with open(config_file, 'rb') as f:
                config_data = tomllib.load(f)
            
            # Update the value
            key_parts = key.split('.')
            current = config_data
            
            # Navigate to the nested dict
            for part in key_parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Set the value
            current[key_parts[-1]] = value
            
            # Write back to file
            try:
                import tomli_w
                with open(config_file, 'wb') as f:
                    tomli_w.dump(config_data, f)
            except ImportError:
                # Fallback to manual writing
                self.app.install_manager._write_toml_manually(config_file, config_data)
                
            return True
        except Exception as e:
            print(f"Error updating config: {str(e)}")
            return False 