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
            "Welcome to arcade_station",
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
                font=("Segoe UI", 24, "bold")
            )
            logo_label.pack(pady=20)
        
        # Welcome text
        welcome_text = ttk.Label(
            welcome_frame,
            text="Welcome to the arcade_station installer! This wizard will guide you through the process of setting up arcade_station on your system.\n\n"
            "Please select Next to continue.",
            wraplength=500,
            justify="center"
        )
        welcome_text.pack(pady=10)
        
        # Installation status
        self.status_frame = ttk.Frame(welcome_frame)
        self.status_frame.pack(fill="x", pady=40)
        
        # This will be updated in on_enter
        self.status_label = ttk.Label(
            self.status_frame,
            wraplength=500,
            justify="center"
        )
        self.status_label.pack(pady=10)
        
        # Install wizard image
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        image_path = os.path.join(project_root, "assets", "images", "photos", "install_wizard.png")
        if os.path.exists(image_path):
            image_label = self.create_image_label(welcome_frame, image_path, size=(400, 300))
            image_label.pack(pady=20)
        
        # Installation mode radio buttons
        self.install_mode_var = tk.StringVar(value="new")
        
        self.install_options_frame = ttk.LabelFrame(
            self.status_frame,
            text="Installation Options",
            padding=10
        )
        
        self.new_install_radio = ttk.Radiobutton(
            self.install_options_frame,
            text="New Installation",
            value="new",
            variable=self.install_mode_var
        )
        
        self.reset_install_radio = ttk.Radiobutton(
            self.install_options_frame,
            text="Reset Existing Installation",
            value="reset",
            variable=self.install_mode_var
        )
        
        self.reconfigure_install_radio = ttk.Radiobutton(
            self.install_options_frame,
            text="Reconfigure Existing Installation",
            value="reconfigure",
            variable=self.install_mode_var
        )
        
        # These will be shown/hidden in on_enter based on installation status
    
    def on_enter(self):
        """Called when the page is shown."""
        # Since installation status will be checked after the user selects an installation location,
        # we'll display a generic welcome message and hide installation options
        self.status_label.config(
            text=""
        )
        
        # Hide installation options frame until we know if Arcade Station is installed
        self.install_options_frame.pack_forget()
        
        # Default to new installation
        self.install_mode_var.set("new")
    
    def on_next(self):
        """Handle next button click."""
        # Since we now check installation in the install location page,
        # we can just proceed with a default new installation setup
        
        # Reset all installation mode flags
        self.app.is_reset_mode = False
        self.app.is_reconfigure_mode = False
        self.app.install_manager.files_copied = False
        self.app.is_installed = False
        
        # Proceed to next page
        super().on_next() 