"""
Game setup overview page for the Arcade Station Installer
"""
import tkinter as tk
from tkinter import ttk

from .base_page import BasePage

class GameSetupPage(BasePage):
    """Overview page for game setup."""
    
    def __init__(self, container, app):
        """Initialize the game setup page."""
        super().__init__(container, app)
        self.set_title(
            "Game Setup",
            "Configure your games"
        )
    
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
        
        itg_icon = ttk.Label(
            itg_frame,
            text="🎮",
            font=("Arial", 16)
        )
        itg_icon.pack(side="left", padx=(5, 10))
        
        itg_text = ttk.Label(
            itg_frame,
            text="ITGMania - Dance game simulator with advanced features",
            wraplength=450,
            justify="left"
        )
        itg_text.pack(side="left", fill="x", expand=True)
        
        # Binary games
        binary_frame = ttk.Frame(types_frame)
        binary_frame.pack(fill="x", pady=5)
        
        binary_icon = ttk.Label(
            binary_frame,
            text="📁",
            font=("Arial", 16)
        )
        binary_icon.pack(side="left", padx=(5, 10))
        
        binary_text = ttk.Label(
            binary_frame,
            text="Binary Games - Executable-based games like OpenITG, NotITG, etc.",
            wraplength=450,
            justify="left"
        )
        binary_text.pack(side="left", fill="x", expand=True)
        
        # MAME games
        mame_frame = ttk.Frame(types_frame)
        mame_frame.pack(fill="x", pady=5)
        
        mame_icon = ttk.Label(
            mame_frame,
            text="🎲",
            font=("Arial", 16)
        )
        mame_icon.pack(side="left", padx=(5, 10))
        
        mame_text = ttk.Label(
            mame_frame,
            text="MAME Games - Arcade games emulated using MAME",
            wraplength=450,
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
                 "1. ITGMania configuration (optional but recommended)\n"
                 "2. Binary games configuration\n"
                 "3. MAME games configuration\n\n"
                 "For each game, you can specify the executable path and an optional "
                 "banner image to display on the marquee.",
            wraplength=500,
            justify="left"
        )
        process_text.pack(fill="x", pady=10)
        
        # Configuration checkbox
        self.configure_games_var = tk.BooleanVar(value=True)
        configure_games_check = ttk.Checkbutton(
            main_frame,
            text="I have games to configure now",
            variable=self.configure_games_var
        )
        configure_games_check.pack(anchor="w", pady=10)
        
        # Help text
        help_text = ttk.Label(
            main_frame,
            text="Note: You can always add more games later by running the installer again.",
            font=("Arial", 9, "italic"),
            foreground="#555555",
            wraplength=500,
            justify="left"
        )
        help_text.pack(anchor="w", pady=(0, 10))
    
    def on_next(self):
        """Handle next button click."""
        # If the user doesn't have games to configure now, skip the game setup pages
        if not self.configure_games_var.get():
            # Find the control config page index
            control_index = self.find_control_config_page_index()
            if control_index != -1:
                # Skip to control config page
                self.on_leave()
                self.app.show_page(control_index)
                return
        
        # Otherwise proceed normally
        super().on_next()
    
    def find_control_config_page_index(self):
        """Find the index of the control config page.
        
        Returns:
            int: Index of the control config page, or -1 if not found
        """
        for i, page in enumerate(self.app.pages):
            if page.__class__.__name__ == "ControlConfigPage":
                return i
        return -1
    
    def save_data(self):
        """Save game setup data."""
        self.app.user_config["configure_games"] = self.configure_games_var.get() 