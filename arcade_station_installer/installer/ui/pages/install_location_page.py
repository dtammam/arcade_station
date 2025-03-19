"""
Installation location page for the Arcade Station Installer
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from .base_page import BasePage

class InstallLocationPage(BasePage):
    """Page for selecting installation location."""
    
    def __init__(self, container, app):
        """Initialize the installation location page."""
        super().__init__(container, app)
        self.set_title(
            "Installation Location",
            "Choose where to install Arcade Station"
        )
    
    def create_widgets(self):
        """Create page-specific widgets."""
        location_frame = ttk.Frame(self.content_frame)
        location_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Instructions
        instruction_label = ttk.Label(
            location_frame,
            text="Select a directory where you want to install Arcade Station. "
                 "This is where all the necessary files will be stored.",
            wraplength=500,
            justify="left"
        )
        instruction_label.pack(anchor="w", pady=(0, 20))
        
        # Default location info
        if self.app.is_installed and self.app.is_reset_mode:
            # If in reset mode, show current installation path
            default_path = self.app.install_manager.get_current_install_path()
            message = "Current installation directory:"
        else:
            # For new installations, suggest a default path
            default_path = self.app.install_manager.get_suggested_install_path()
            message = "Suggested installation directory:"
        
        default_label = ttk.Label(
            location_frame,
            text=message,
            wraplength=500,
            justify="left"
        )
        default_label.pack(anchor="w", pady=(0, 5))
        
        # Path entry
        path_frame = ttk.Frame(location_frame)
        path_frame.pack(fill="x", pady=5)
        
        self.path_var = tk.StringVar(value=default_path)
        
        path_entry = ttk.Entry(
            path_frame,
            textvariable=self.path_var,
            width=50
        )
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_button = ttk.Button(
            path_frame,
            text="Browse...",
            command=self.browse_location
        )
        browse_button.pack(side="right")
        
        # Space requirements
        requirements_frame = ttk.LabelFrame(
            location_frame,
            text="Requirements",
            padding=(10, 5)
        )
        requirements_frame.pack(fill="x", pady=20)
        
        space_label = ttk.Label(
            requirements_frame,
            text="Disk space required: Approximately 50 MB (excluding games)",
            wraplength=500,
            justify="left"
        )
        space_label.pack(anchor="w", pady=5)
        
        permission_label = ttk.Label(
            requirements_frame,
            text="You must have write permissions to the selected directory.",
            wraplength=500,
            justify="left"
        )
        permission_label.pack(anchor="w", pady=5)
        
        # Warning about existing installation
        if self.app.is_installed and not self.app.is_reset_mode:
            warning_frame = ttk.Frame(location_frame)
            warning_frame.pack(fill="x", pady=10)
            
            warning_label = ttk.Label(
                warning_frame,
                text="Warning: A new installation will not remove the existing installation. "
                     "To avoid conflicts, consider using the same location as the existing installation "
                     "or completely removing the old installation first.",
                wraplength=500,
                foreground="red",
                justify="left"
            )
            warning_label.pack(anchor="w")
    
    def browse_location(self):
        """Open a directory browser dialog."""
        current_path = self.path_var.get()
        initial_dir = current_path if os.path.isdir(current_path) else os.path.expanduser("~")
        
        selected_dir = filedialog.askdirectory(
            title="Select Installation Directory",
            initialdir=initial_dir
        )
        
        if selected_dir:
            self.path_var.set(selected_dir)
    
    def validate(self):
        """Validate the installation path."""
        path = self.path_var.get().strip()
        
        if not path:
            messagebox.showerror(
                "Invalid Path", 
                "Please enter a valid installation path."
            )
            return False
        
        # Check if path exists and can be written to
        if not os.path.isdir(path):
            try:
                os.makedirs(path, exist_ok=True)
            except Exception as e:
                messagebox.showerror(
                    "Permission Error", 
                    f"Cannot create directory: {e}"
                )
                return False
        
        # Check write permissions by trying to create a test file
        test_file = os.path.join(path, ".arcade_station_test")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
        except Exception as e:
            messagebox.showerror(
                "Permission Error", 
                f"Cannot write to the selected directory: {e}"
            )
            return False
        
        return True
    
    def save_data(self):
        """Save the installation path."""
        self.app.user_config["install_path"] = self.path_var.get().strip() 