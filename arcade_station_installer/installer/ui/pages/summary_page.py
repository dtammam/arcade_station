"""
Summary page for the Arcade Station Installer
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox
import json

from .base_page import BasePage

class SummaryPage(BasePage):
    """Summary page showing all configuration before installation."""
    
    def __init__(self, container, app):
        """Initialize the summary page."""
        super().__init__(container, app)
        self.set_title(
            "Installation Summary",
            "Review your configuration before installation"
        )
    
    def on_page_show(self):
        """Called when the page is shown to the user."""
        # Clear the current summary and rebuild it with the latest configuration
        self.update_summary_text()
    
    def create_widgets(self):
        """Create page-specific widgets."""
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Introduction
        intro_text = ttk.Label(
            main_frame,
            text="Review your Arcade Station configuration before installation. "
                 "If you need to make changes, use the 'Previous' button to navigate back.",
            wraplength=500,
            justify="left"
        )
        intro_text.pack(anchor="w", pady=(0, 15))
        
        # Configuration summary frame
        summary_frame = ttk.LabelFrame(
            main_frame,
            text="Configuration Summary",
            padding=(10, 5)
        )
        summary_frame.pack(fill="both", expand=True, pady=10)
        
        # Create a frame with scrollbar for the summary
        canvas_frame = ttk.Frame(summary_frame)
        canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(
            canvas_frame,
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            canvas_frame,
            orient="vertical",
            command=self.canvas.yview
        )
        
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Summary text
        self.summary_text = tk.Text(
            self.scrollable_frame,
            wrap="word",
            width=80,
            height=25,
            font=("TkDefaultFont", 10),
            padx=10,
            pady=10,
            state="disabled"
        )
        self.summary_text.pack(fill="both", expand=True)
        
        # Configure canvas to expand with window
        main_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(width=e.width - 50)
        )
        
        # Export configuration button
        export_frame = ttk.Frame(main_frame)
        export_frame.pack(fill="x", pady=10)
        
        export_button = ttk.Button(
            export_frame,
            text="Export Configuration",
            command=self.export_config
        )
        export_button.pack(side="right")
        
        # Ready to install label
        ready_label = ttk.Label(
            main_frame,
            text="When you're ready to install, click 'Install' to begin the installation process.",
            font=("TkDefaultFont", 10, "bold"),
            wraplength=500,
            justify="left"
        )
        ready_label.pack(anchor="w", pady=10)
    
    def update_summary_text(self):
        """Update the summary text with the current configuration."""
        self.summary_text.config(state="normal")
        self.summary_text.delete(1.0, tk.END)
        
        # Helper function to add sections
        def add_section(title, content, level=1):
            if level == 1:
                self.summary_text.insert(tk.END, f"\n{title}\n", "section1")
                self.summary_text.insert(tk.END, "="*len(title) + "\n\n")
            elif level == 2:
                self.summary_text.insert(tk.END, f"\n{title}\n", "section2")
                self.summary_text.insert(tk.END, "-"*len(title) + "\n\n")
            else:
                self.summary_text.insert(tk.END, f"\n{title}:\n\n", "section3")
            
            if isinstance(content, dict):
                for key, value in content.items():
                    if isinstance(value, dict):
                        add_section(key, value, level+1)
                    elif isinstance(value, list):
                        self.summary_text.insert(tk.END, f"{key}: \n")
                        for item in value:
                            if isinstance(item, dict):
                                for k, v in item.items():
                                    self.summary_text.insert(tk.END, f"  - {k}: {v}\n")
                            else:
                                self.summary_text.insert(tk.END, f"  - {item}\n")
                        self.summary_text.insert(tk.END, "\n")
                    else:
                        display_value = self._format_value(value)
                        self.summary_text.insert(tk.END, f"{key}: {display_value}\n")
            elif isinstance(content, list):
                for item in content:
                    self.summary_text.insert(tk.END, f"- {item}\n")
            else:
                self.summary_text.insert(tk.END, f"{content}\n")
        
        # Create tag configurations
        self.summary_text.tag_configure("section1", font=("TkDefaultFont", 12, "bold"))
        self.summary_text.tag_configure("section2", font=("TkDefaultFont", 11, "bold"))
        self.summary_text.tag_configure("section3", font=("TkDefaultFont", 10, "bold"))
        
        # Add installation information
        self.summary_text.insert(tk.END, "ARCADE STATION INSTALLATION SUMMARY\n", "section1")
        self.summary_text.insert(tk.END, "="*35 + "\n\n")
        
        # Installation path
        install_path = self.app.user_config.get("install_path", "")
        self.summary_text.insert(tk.END, f"Installation Path: {install_path}\n\n")
        
        # Platform specific settings
        platform = "Windows" if self.app.install_manager.is_windows else "Linux" if self.app.install_manager.is_linux else "MacOS"
        self.summary_text.insert(tk.END, f"Platform: {platform}\n")
        
        if self.app.install_manager.is_windows:
            self.summary_text.insert(tk.END, f"Kiosk Mode: {'Enabled' if self.app.user_config.get('enable_kiosk_mode', False) else 'Disabled'}\n")
            
            if self.app.user_config.get('enable_kiosk_mode', False):
                self.summary_text.insert(tk.END, "Kiosk Mode Settings:\n")
                self.summary_text.insert(tk.END, f"  - Username: {self.app.user_config.get('kiosk_username', '')}\n")
                self.summary_text.insert(tk.END, f"  - Auto Login: {'Yes' if self.app.user_config.get('kiosk_auto_login', False) else 'No'}\n")
                self.summary_text.insert(tk.END, f"  - Replace Shell: {'Yes' if self.app.user_config.get('kiosk_replace_shell', False) else 'No'}\n")
                self.summary_text.insert(tk.END, f"  - Disable Task Manager: {'Yes' if self.app.user_config.get('kiosk_disable_task_manager', False) else 'No'}\n")
                self.summary_text.insert(tk.END, f"  - Hide Cursor: {'Yes' if self.app.user_config.get('kiosk_hide_cursor', False) else 'No'}\n")
                self.summary_text.insert(tk.END, "\n")
            
            startup_options = []
            if self.app.user_config.get("add_to_startup", False):
                startup_options.append("Add to Windows Startup")
            if self.app.user_config.get("create_desktop_shortcut", False):
                startup_options.append("Create Desktop Shortcut")
            if self.app.user_config.get("create_start_menu", False):
                startup_options.append("Create Start Menu Entry")
            
            if startup_options:
                self.summary_text.insert(tk.END, "Windows Options:\n")
                for option in startup_options:
                    self.summary_text.insert(tk.END, f"  - {option}\n")
        
        # Display settings
        self.summary_text.insert(tk.END, "\n")
        display_settings = self.app.user_config.get("display", {})
        if display_settings:
            resolution = display_settings.get("resolution", "1920x1080")
            fullscreen = display_settings.get("fullscreen", True)
            vsync = display_settings.get("vsync", True)
            multi_monitor = display_settings.get("use_multiple_monitors", False)
            
            self.summary_text.insert(tk.END, "Display Settings:\n")
            self.summary_text.insert(tk.END, f"  - Resolution: {resolution}\n")
            self.summary_text.insert(tk.END, f"  - Fullscreen: {'Yes' if fullscreen else 'No'}\n")
            self.summary_text.insert(tk.END, f"  - VSync: {'Enabled' if vsync else 'Disabled'}\n")
            self.summary_text.insert(tk.END, f"  - Multi-monitor: {'Yes' if multi_monitor else 'No'}\n")
            
            if multi_monitor:
                monitor_config = display_settings.get("monitor_config", {})
                if monitor_config:
                    self.summary_text.insert(tk.END, "  - Monitor Configuration:\n")
                    for monitor, config in monitor_config.items():
                        self.summary_text.insert(tk.END, f"    - {monitor}: {config}\n")
        
        # Add sections for each major configuration component
        self._add_game_configs()
        self._add_controls_config()
        self._add_lighting_config()
        self._add_utilities_config()
        
        # Set text to read-only
        self.summary_text.config(state="disabled")
    
    def _format_value(self, value):
        """Format a value for display in the summary."""
        if isinstance(value, bool):
            return "Yes" if value else "No"
        return str(value)
    
    def _add_game_configs(self):
        """Add game configuration sections to the summary."""
        # ITGMania
        itgmania_config = self.app.user_config.get("itgmania", {})
        if itgmania_config.get("enabled", False):
            self.summary_text.insert(tk.END, "\nITGMania Integration\n", "section2")
            self.summary_text.insert(tk.END, "-------------------\n\n")
            
            itg_path = itgmania_config.get("path", "")
            self.summary_text.insert(tk.END, f"Path: {itg_path}\n")
            
            use_default_image = itgmania_config.get("use_default_image", True)
            custom_image = itgmania_config.get("custom_image", "")
            
            self.summary_text.insert(tk.END, f"Banner: {'Default' if use_default_image else custom_image}\n")
            
            noteskins = itgmania_config.get("noteskins", [])
            if noteskins:
                self.summary_text.insert(tk.END, "Noteskins:\n")
                for noteskin in noteskins:
                    self.summary_text.insert(tk.END, f"  - {noteskin}\n")
        
        # Binary Games
        binary_games = self.app.user_config.get("binary_games", {})
        if binary_games:
            self.summary_text.insert(tk.END, "\nBinary Games\n", "section2")
            self.summary_text.insert(tk.END, "------------\n\n")
            
            for game_id, game in binary_games.items():
                name = game.get("display_name", "")
                executable = game.get("executable", "")
                banner = game.get("banner", "")
                
                self.summary_text.insert(tk.END, f"Game: {name}\n")
                self.summary_text.insert(tk.END, f"  - ID: {game_id}\n")
                self.summary_text.insert(tk.END, f"  - Executable: {executable}\n")
                if banner:
                    self.summary_text.insert(tk.END, f"  - Banner: {banner}\n")
                self.summary_text.insert(tk.END, "\n")
        
        # MAME Games
        mame_config = self.app.user_config.get("mame_path", "")
        mame_games = self.app.user_config.get("mame_games", {})
        
        if mame_config or mame_games:
            self.summary_text.insert(tk.END, "\nMAME Games\n", "section2")
            self.summary_text.insert(tk.END, "----------\n\n")
            
            if mame_config:
                self.summary_text.insert(tk.END, f"MAME Path: {mame_config}\n")
                
                mame_inipath = self.app.user_config.get("mame_inipath", "")
                if mame_inipath:
                    self.summary_text.insert(tk.END, f"MAME INI Path: {mame_inipath}\n")
            
            if mame_games:
                self.summary_text.insert(tk.END, "\nConfigured MAME Games:\n")
                for game_id, game in mame_games.items():
                    name = game.get("display_name", "")
                    rom = game.get("rom", "")
                    state = game.get("state", "")
                    
                    self.summary_text.insert(tk.END, f"Game: {name}\n")
                    self.summary_text.insert(tk.END, f"  - ROM: {rom}\n")
                    self.summary_text.insert(tk.END, f"  - Save State: {state}\n")
                    self.summary_text.insert(tk.END, "\n")
    
    def _add_controls_config(self):
        """Add controls configuration to the summary."""
        controls_config = self.app.user_config.get("controls", {})
        if controls_config:
            self.summary_text.insert(tk.END, "\nControls Configuration\n", "section2")
            self.summary_text.insert(tk.END, "---------------------\n\n")
            
            # Input types
            input_types = []
            if controls_config.get("use_arcade_controls", False):
                input_types.append("Arcade Controls")
            if controls_config.get("use_gamepad", False):
                input_types.append("Gamepad")
            if controls_config.get("use_keyboard", False):
                input_types.append("Keyboard")
            
            if input_types:
                self.summary_text.insert(tk.END, "Input Types: " + ", ".join(input_types) + "\n\n")
            
            # Arcade controls
            arcade_config = controls_config.get("arcade", {})
            if arcade_config:
                self.summary_text.insert(tk.END, "Arcade Controls:\n")
                self.summary_text.insert(tk.END, f"  - Players: {arcade_config.get('players', 2)}\n")
                self.summary_text.insert(tk.END, f"  - Buttons per player: {arcade_config.get('buttons_per_player', 8)}\n")
                self.summary_text.insert(tk.END, f"  - Interface: {arcade_config.get('interface', 'xinput')}\n")
                
                custom_mapping = arcade_config.get("custom_mapping_file", "")
                if custom_mapping:
                    self.summary_text.insert(tk.END, f"  - Custom mapping: {custom_mapping}\n")
                
                self.summary_text.insert(tk.END, "\n")
            
            # Gamepad
            gamepad_config = controls_config.get("gamepad", {})
            if gamepad_config:
                self.summary_text.insert(tk.END, "Gamepad:\n")
                self.summary_text.insert(tk.END, f"  - Maximum gamepads: {gamepad_config.get('max_gamepads', 4)}\n")
                self.summary_text.insert(tk.END, f"  - Preferred type: {gamepad_config.get('preferred_type', 'xbox')}\n")
                self.summary_text.insert(tk.END, "\n")
            
            # Keyboard
            keyboard_config = controls_config.get("keyboard", {})
            if keyboard_config:
                self.summary_text.insert(tk.END, "Keyboard:\n")
                self.summary_text.insert(tk.END, f"  - Layout: {keyboard_config.get('layout', 'us')}\n")
                self.summary_text.insert(tk.END, f"  - Standard mappings: {'Yes' if keyboard_config.get('use_standard_mappings', True) else 'No'}\n")
                
                custom_mapping = keyboard_config.get("custom_mapping_file", "")
                if custom_mapping:
                    self.summary_text.insert(tk.END, f"  - Custom mapping: {custom_mapping}\n")
    
    def _add_lighting_config(self):
        """Add lighting configuration to the summary."""
        lighting_config = self.app.user_config.get("lighting", {})
        if lighting_config and lighting_config.get("enabled", False):
            self.summary_text.insert(tk.END, "\nLighting Configuration\n", "section2")
            self.summary_text.insert(tk.END, "----------------------\n\n")
            
            self.summary_text.insert(tk.END, f"System: {lighting_config.get('system', 'arduino')}\n")
            self.summary_text.insert(tk.END, f"Brightness: {lighting_config.get('brightness', 75)}%\n")
            self.summary_text.insert(tk.END, f"Default Animation: {lighting_config.get('default_animation', 'rainbow')}\n")
            
            # Arduino settings
            arduino_config = lighting_config.get("arduino", {})
            if arduino_config:
                self.summary_text.insert(tk.END, "\nArduino Settings:\n")
                self.summary_text.insert(tk.END, f"  - Port: {arduino_config.get('port', '')}\n")
                self.summary_text.insert(tk.END, f"  - Number of LEDs: {arduino_config.get('num_leds', 60)}\n")
                
                sketch = arduino_config.get("sketch", "")
                if sketch:
                    self.summary_text.insert(tk.END, f"  - Sketch: {sketch}\n")
            
            # Button lighting
            button_lighting = lighting_config.get("button_lighting", {})
            if button_lighting and button_lighting.get("enabled", False):
                self.summary_text.insert(tk.END, "\nButton Lighting:\n")
                player_colors = button_lighting.get("player_colors", [])
                for i, color in enumerate(player_colors, 1):
                    self.summary_text.insert(tk.END, f"  - Player {i}: {color}\n")
            
            # Cabinet layout
            cabinet = lighting_config.get("cabinet", {})
            if cabinet:
                self.summary_text.insert(tk.END, "\nCabinet Layout:\n")
                self.summary_text.insert(tk.END, f"  - Marquee: {'Yes' if cabinet.get('has_marquee', True) else 'No'}\n")
                self.summary_text.insert(tk.END, f"  - Control Panel Lighting: {'Yes' if cabinet.get('has_cp_lighting', True) else 'No'}\n")
                self.summary_text.insert(tk.END, f"  - Speaker Lighting: {'Yes' if cabinet.get('has_speaker_lighting', False) else 'No'}\n")
            
            # Custom config
            custom_config = lighting_config.get("custom_config", "")
            if custom_config:
                self.summary_text.insert(tk.END, f"\nCustom Configuration: {custom_config}\n")
    
    def _add_utilities_config(self):
        """Add utilities configuration to the summary."""
        utilities_config = self.app.user_config.get("utilities", {})
        if utilities_config:
            self.summary_text.insert(tk.END, "\nUtilities Configuration\n", "section2")
            self.summary_text.insert(tk.END, "-----------------------\n\n")
            
            # System utilities
            system = utilities_config.get("system", {})
            if system:
                self.summary_text.insert(tk.END, "System Utilities:\n")
                self.summary_text.insert(tk.END, f"  - Enabled: {'Yes' if system.get('enabled', True) else 'No'}\n")
                self.summary_text.insert(tk.END, f"  - Auto Updates: {'Yes' if system.get('auto_updates', True) else 'No'}\n")
                self.summary_text.insert(tk.END, f"  - System Monitoring: {'Yes' if system.get('system_monitoring', True) else 'No'}\n")
                self.summary_text.insert(tk.END, f"  - Error Reporting: {'Yes' if system.get('error_reporting', True) else 'No'}\n")
                
                log_dir = system.get("log_directory", "")
                if log_dir:
                    self.summary_text.insert(tk.END, f"  - Custom Log Directory: {log_dir}\n")
                
                self.summary_text.insert(tk.END, "\n")
            
            # Backup settings
            backup = utilities_config.get("backup", {})
            if backup and backup.get("enabled", False):
                self.summary_text.insert(tk.END, "Backup Settings:\n")
                self.summary_text.insert(tk.END, f"  - Frequency: {backup.get('frequency', 'weekly')}\n")
                self.summary_text.insert(tk.END, f"  - Directory: {backup.get('directory', '')}\n")
                self.summary_text.insert(tk.END, f"  - Keep Backups: {backup.get('keep_backups', 5)}\n")
                self.summary_text.insert(tk.END, "\n")
            
            # Maintenance tools
            tools = utilities_config.get("maintenance_tools", {})
            if tools:
                enabled_tools = []
                if tools.get("rom_validator", False):
                    enabled_tools.append("ROM Validator")
                if tools.get("input_tester", False):
                    enabled_tools.append("Input Tester")
                if tools.get("system_cleaner", False):
                    enabled_tools.append("System Cleaner")
                if tools.get("config_editor", False):
                    enabled_tools.append("Configuration Editor")
                if tools.get("media_manager", False):
                    enabled_tools.append("Media Manager")
                if tools.get("quick_service", False):
                    enabled_tools.append("Quick Service Menu")
                
                if enabled_tools:
                    self.summary_text.insert(tk.END, "Maintenance Tools:\n")
                    for tool in enabled_tools:
                        self.summary_text.insert(tk.END, f"  - {tool}\n")
                    self.summary_text.insert(tk.END, "\n")
            
            # Advanced options
            advanced = utilities_config.get("advanced", {})
            if advanced:
                self.summary_text.insert(tk.END, "Advanced Options:\n")
                self.summary_text.insert(tk.END, f"  - Maintenance Key: {advanced.get('maintenance_key', 'F10')}\n")
                
                if "maintenance_password" in advanced:
                    self.summary_text.insert(tk.END, "  - Maintenance Password: [Set]\n")
                
                if "maintenance_hotkey" in advanced:
                    self.summary_text.insert(tk.END, f"  - Maintenance Hotkey: {advanced['maintenance_hotkey']}\n")
                
                if "exit_hotkey" in advanced:
                    self.summary_text.insert(tk.END, f"  - Exit Hotkey: {advanced['exit_hotkey']}\n")
                
                if "frontend_timeout" in advanced:
                    self.summary_text.insert(tk.END, f"  - Frontend Timeout: {advanced['frontend_timeout']} seconds\n")
                
                if "maintenance_password_hash" in advanced:
                    self.summary_text.insert(tk.END, "  - Maintenance Password: [Securely Stored]\n")
                
                if "custom_scripts_enabled" in advanced and advanced["custom_scripts_enabled"]:
                    self.summary_text.insert(tk.END, "  - Custom Scripts: Enabled\n")
                
                if "scripts_directory" in advanced:
                    self.summary_text.insert(tk.END, f"  - Scripts Directory: {advanced['scripts_directory']}\n")
                
                self.summary_text.insert(tk.END, "\n")
            
            # Custom scripts
            scripts = utilities_config.get("custom_scripts", {})
            if scripts and scripts.get("enabled", False):
                self.summary_text.insert(tk.END, "Custom Scripts:\n")
                self.summary_text.insert(tk.END, f"  - Directory: {scripts.get('directory', '')}\n")
    
    def export_config(self):
        """Export the configuration to a JSON file."""
        save_path = tk.filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Configuration"
        )
        
        if not save_path:
            return
        
        try:
            with open(save_path, 'w') as f:
                json.dump(self.app.user_config, f, indent=4)
            
            messagebox.showinfo(
                "Export Successful",
                f"Configuration exported to {save_path}"
            )
        except Exception as e:
            messagebox.showerror(
                "Export Failed",
                f"Failed to export configuration: {str(e)}"
            )
    
    def validate(self):
        """Validate the page."""
        # Nothing to validate on the summary page
        return True
    
    def save_data(self):
        """Save data from the page."""
        # Nothing to save on the summary page
        pass 