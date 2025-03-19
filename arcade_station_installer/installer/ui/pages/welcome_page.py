"""
Welcome page for the Arcade Station Installer
"""
import tkinter as tk
from tkinter import ttk
import os

from .base_page import BasePage
from ... import get_platform_name

class WelcomePage(BasePage):
    """Welcome page with installation detection."""
    
    def __init__(self, container, app):
        """Initialize the welcome page."""
        super().__init__(container, app)
        self.set_title(
            "Welcome to Arcade Station",
            f"Installation for {get_platform_name()}"
        )
        
        # Disable back button on first page
        self.set_back_button_state(False)
    
    def create_widgets(self):
        """Create page-specific widgets."""
        # Welcome message
        welcome_frame = ttk.Frame(self.content_frame)
        welcome_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Logo or image if available
        try:
            from PIL import Image, ImageTk
            logo_path = os.path.join(self.app.install_manager.resources_dir, "logo.png")
            if os.path.exists(logo_path):
                img = Image.open(logo_path)
                img = img.resize((200, 200), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                logo_label = ttk.Label(welcome_frame, image=photo)
                logo_label.image = photo  # Keep a reference
                logo_label.pack(pady=20)
        except ImportError:
            # PIL not available, use text instead
            logo_label = ttk.Label(
                welcome_frame, 
                text="ARCADE STATION",
                font=("Arial", 24, "bold")
            )
            logo_label.pack(pady=20)
        
        # Welcome text
        welcome_text = ttk.Label(
            welcome_frame,
            text="Welcome to the Arcade Station installer! This wizard will guide you through "
                 "the process of setting up Arcade Station on your system.",
            wraplength=500,
            justify="center"
        )
        welcome_text.pack(pady=10)
        
        # Installation status
        self.status_frame = ttk.Frame(welcome_frame)
        self.status_frame.pack(fill="x", pady=20)
        
        # This will be updated in on_enter
        self.status_label = ttk.Label(
            self.status_frame,
            wraplength=500,
            justify="center"
        )
        self.status_label.pack(pady=10)
        
        # Installation mode radio buttons
        self.install_mode_var = tk.StringVar(value="new")
        
        self.new_install_radio = ttk.Radiobutton(
            self.status_frame,
            text="New Installation",
            value="new",
            variable=self.install_mode_var
        )
        
        self.reset_install_radio = ttk.Radiobutton(
            self.status_frame,
            text="Reset Existing Installation",
            value="reset",
            variable=self.install_mode_var
        )
        
        # These will be shown/hidden in on_enter based on installation status
    
    def on_enter(self):
        """Called when the page is shown."""
        # Check if Arcade Station is already installed
        is_installed = self.app.is_installed
        
        if is_installed:
            self.status_label.config(
                text="Arcade Station is already installed on this system. "
                     "You can either reset specific settings or perform a new installation."
            )
            
            # Show installation mode options
            self.new_install_radio.pack(anchor="w", padx=100, pady=5)
            self.reset_install_radio.pack(anchor="w", padx=100, pady=5)
            
            # Default to reset mode
            self.install_mode_var.set("reset")
        else:
            self.status_label.config(
                text="Arcade Station is not currently installed on this system. "
                     "This wizard will guide you through the installation process."
            )
            
            # Hide installation mode options
            self.new_install_radio.pack_forget()
            self.reset_install_radio.pack_forget()
    
    def on_next(self):
        """Handle next button click."""
        # Set reset mode based on selection
        if self.app.is_installed and self.install_mode_var.get() == "reset":
            self.app.set_reset_mode(True)
        else:
            self.app.set_reset_mode(False)
        
        # Decide which pages to include in the flow
        self.app.decide_next_page_flow()
        
        # Proceed to next page
        super().on_next() 