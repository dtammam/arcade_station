"""
Game setup overview page for the Arcade Station Installer
"""
import tkinter as tk
from tkinter import ttk
import os
import tomllib
import logging

from .base_page import BasePage

class GameSetupPage(BasePage):
    """Overview page for game setup."""
    
    def __init__(self, container, app):
        """Initialize the game setup page."""
        # Initialize icon paths before parent's __init__
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        self.icon_paths = {
            'itgmania': os.path.join(project_root, "assets", "images", "icons", "itgmania_logo.png"),
            'binary': os.path.join(project_root, "assets", "images", "icons", "binary_logo.png"),
            'mame': os.path.join(project_root, "assets", "images", "icons", "mame_logo.png")
        }
        
        # Now call parent's __init__
        super().__init__(container, app)
        self.set_title(
            "Game Setup",
            "Configure your games"
        )
        
    def on_enter(self):
        """Called when the page is shown."""
        # If in reconfigure mode and we have existing games, pre-check the checkbox
        if hasattr(self.app, 'is_reconfigure_mode') and self.app.is_reconfigure_mode:
            installed_games_path = os.path.join(self.app.user_config.get("install_path", ""), "config", "installed_games.toml")
            if os.path.exists(installed_games_path):
                try:
                    with open(installed_games_path, "rb") as f:
                        installed_games = tomllib.load(f)
                        if installed_games.get("games"):
                            self.has_games_var.set(True)
                except Exception as e:
                    logging.warning(f"Failed to load existing installed_games.toml: {e}")
    
    def create_widgets(self):
        """Create page-specific widgets."""
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Overview text
        intro_text = ttk.Label(
            main_frame,
            text="Arcade Station can manage various games for your arcade cabinet. "
                 "In the following steps, you'll configure which games you want to include.",
            wraplength=500,
            justify="left"
        )
        intro_text.pack(anchor="w", pady=(0, 20))
        
        # Game types frame
        types_frame = ttk.LabelFrame(
            main_frame,
            text="Game Types",
            padding=(10, 5)
        )
        types_frame.pack(fill="x", pady=10)
        
        # ITGMania
        itg_frame = ttk.Frame(types_frame)
        itg_frame.pack(fill="x", pady=5)
        
        itg_icon = self.create_image_label(itg_frame, self.icon_paths['itgmania'], size=(32, 32))
        itg_icon.pack(side="left", padx=(5, 10))
        
        itg_text = ttk.Label(
            itg_frame,
            text="Built on StepMania 5.1, ITGMania powers high-performance rhythm gaming with the iconic Simply Love interface.",
            wraplength=750,
            justify="left"
        )
        itg_text.pack(side="left", fill="x", expand=True)
        
        # Binary games
        binary_frame = ttk.Frame(types_frame)
        binary_frame.pack(fill="x", pady=5)
        
        binary_icon = self.create_image_label(binary_frame, self.icon_paths['binary'], size=(32, 32))
        binary_icon.pack(side="left", padx=(5, 10))
        
        binary_text = ttk.Label(
            binary_frame,
            text="Whether it's Call of Duty, Grand Theft Auto, or any other binary game, binary games boot via .exe, .bat, or .ps1 files.",
            wraplength=750,
            justify="left"
        )
        binary_text.pack(side="left", fill="x", expand=True)
        
        # MAME games
        mame_frame = ttk.Frame(types_frame)
        mame_frame.pack(fill="x", pady=5)
        
        mame_icon = self.create_image_label(mame_frame, self.icon_paths['mame'], size=(32, 32))
        mame_icon.pack(side="left", padx=(5, 10))
        
        mame_text = ttk.Label(
            mame_frame,
            text="From Pac Man to Dig Dug, all the way to DDR EXTREME - MAME emulates classic arcade games on PC.",
            wraplength=750,
            justify="left"
        )
        mame_text.pack(side="left", fill="x", expand=True)
        
        # Setup process
        process_frame = ttk.LabelFrame(
            main_frame,
            text="Setup Process",
            padding=(10, 5)
        )
        process_frame.pack(fill="x", pady=20)
        
        process_text = ttk.Label(
            process_frame,
            text="In the next few screens, you'll configure each type of game:\n\n"
                 "- For each game, you can specify the executable path and an optional image for the menu and marquee.\n\n"
                 "- Your input will be saved to configuration files and can be updated later.\n\n"
                 "- Everything is optional. You can uncheck the box below to skip game configuration and preserve existing settings.",
            wraplength=750,
            justify="left"
        )
        process_text.pack(fill="x", pady=10)
        
        # Does the user have games already?
        self.has_games_var = tk.BooleanVar(value=True)
        has_games = ttk.Checkbutton(
            main_frame,
            text="I would like to configure games now",
            variable=self.has_games_var
        )
        has_games.pack(anchor="w", pady=10)
        
        # Help text
        help_text = ttk.Label(
            main_frame,
            text="Note: You can skip game setup. You can always add more games later by running the installer again.",
            font=("Arial", 9, "italic"),
            foreground="#555555",
            wraplength=750,
            justify="left"
        )
        help_text.pack(anchor="w", pady=(0, 10))
    
    def on_next(self):
        """Handle next button click."""
        # If the user doesn't have games to configure now, skip to key bindings
        if not self.has_games_var.get():
            # Find the key bindings page index
            key_bindings_index = self.find_key_bindings_page_index()
            if key_bindings_index != -1:
                self.on_leave()
                self.app.show_page(key_bindings_index)
                return
        
        # Otherwise proceed normally
        super().on_next()
    
    def find_key_bindings_page_index(self):
        """Find the index of the key bindings page.
        
        Returns:
            int: Index of the key bindings page, or -1 if not found
        """
        for i, page in enumerate(self.app.pages):
            if page.__class__.__name__ == "KeyBindingsPage":
                return i
        return -1
    
    def save_data(self):
        """Save game setup data."""
        self.app.user_config["skip_games"] = not self.has_games_var.get() 