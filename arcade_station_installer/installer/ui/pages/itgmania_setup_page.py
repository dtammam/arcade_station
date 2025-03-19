"""
ITGMania setup page for the Arcade Station Installer
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from .base_page import BasePage

class ITGManiaSetupPage(BasePage):
    """Page for setting up ITGMania integration."""
    
    def __init__(self, container, app):
        """Initialize the ITGMania setup page."""
        super().__init__(container, app)
        self.set_title(
            "ITGMania Setup",
            "Configure ITGMania integration"
        )
        self.default_image_path = ""
    
    def create_widgets(self):
        """Create page-specific widgets."""
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Introduction
        intro_text = ttk.Label(
            main_frame,
            text="ITGMania is a popular rhythm game simulator. Arcade Station can integrate "
                 "deeply with ITGMania to provide enhanced features, such as displaying "
                 "song-specific information on the marquee display.",
            wraplength=500,
            justify="left"
        )
        intro_text.pack(anchor="w", pady=(0, 20))
        
        # Use ITGMania checkbox
        self.use_itgmania_var = tk.BooleanVar(value=True)
        use_itgmania = ttk.Checkbutton(
            main_frame,
            text="I want to use ITGMania with Arcade Station",
            variable=self.use_itgmania_var,
            command=self.toggle_itgmania_settings
        )
        use_itgmania.pack(anchor="w", pady=(0, 10))
        
        # ITGMania settings frame
        self.itgmania_frame = ttk.LabelFrame(
            main_frame,
            text="ITGMania Configuration",
            padding=(10, 5)
        )
        
        # ITGMania executable path
        path_frame = ttk.Frame(self.itgmania_frame)
        path_frame.pack(fill="x", pady=5)
        
        path_label = ttk.Label(
            path_frame,
            text="ITGMania Path:",
            width=15
        )
        path_label.pack(side="left", padx=(0, 5))
        
        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(
            path_frame,
            textvariable=self.path_var,
            width=40
        )
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_button = ttk.Button(
            path_frame,
            text="Browse...",
            command=self.browse_itgmania
        )
        browse_button.pack(side="right")
        
        # ITGMania image
        image_frame = ttk.Frame(self.itgmania_frame)
        image_frame.pack(fill="x", pady=5)
        
        image_label = ttk.Label(
            image_frame,
            text="Banner Image:",
            width=15
        )
        image_label.pack(side="left", padx=(0, 5))
        
        self.image_var = tk.StringVar()
        self.image_entry = ttk.Entry(
            image_frame,
            textvariable=self.image_var,
            width=40
        )
        self.image_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.browse_image_button = ttk.Button(
            image_frame,
            text="Browse...",
            command=self.browse_image
        )
        self.browse_image_button.pack(side="right")
        
        # Use default Simply Love theme image
        self.use_default_image_var = tk.BooleanVar(value=True)
        use_default_image = ttk.Checkbutton(
            self.itgmania_frame,
            text="Use default Simply Love theme image",
            variable=self.use_default_image_var,
            command=self.toggle_default_image
        )
        use_default_image.pack(anchor="w", pady=5)
        
        # Dynamic marquee integration
        self.marquee_frame = ttk.LabelFrame(
            main_frame,
            text="Dynamic Marquee Integration",
            padding=(10, 5)
        )
        
        # Explanation
        marquee_text = ttk.Label(
            self.marquee_frame,
            text="ITGMania can display song-specific information on the marquee display. "
                 "To enable this feature, Arcade Station includes a special module for "
                 "the Simply Love theme that must be installed.",
            wraplength=450,
            justify="left"
        )
        marquee_text.pack(anchor="w", pady=5)
        
        # Install module checkbox
        self.install_module_var = tk.BooleanVar(value=True)
        install_module = ttk.Checkbutton(
            self.marquee_frame,
            text="Install Simply Love dynamic marquee module",
            variable=self.install_module_var
        )
        install_module.pack(anchor="w", pady=5)
        
        # Set initial state
        self.toggle_itgmania_settings()
        self.toggle_default_image()
    
    def toggle_itgmania_settings(self):
        """Show or hide ITGMania settings based on checkbox state."""
        if self.use_itgmania_var.get():
            self.itgmania_frame.pack(fill="x", pady=10)
            self.marquee_frame.pack(fill="x", pady=10)
        else:
            self.itgmania_frame.pack_forget()
            self.marquee_frame.pack_forget()
    
    def toggle_default_image(self):
        """Enable or disable the image entry based on default image checkbox."""
        if self.use_default_image_var.get():
            self.image_var.set("")
            self.image_entry.config(state="disabled")
            self.browse_image_button.config(state="disabled")
        else:
            self.image_entry.config(state="normal")
            self.browse_image_button.config(state="normal")
    
    def browse_itgmania(self):
        """Open a file browser dialog for selecting the ITGMania executable."""
        filetypes = [
            ("Executable files", "*.exe")
        ] if self.app.install_manager.is_windows else [
            ("All files", "*")
        ]
        
        initial_dir = os.path.dirname(self.path_var.get()) if self.path_var.get() else os.path.expanduser("~")
        
        if self.app.install_manager.is_windows:
            file_path = filedialog.askopenfilename(
                title="Select ITGMania Executable",
                filetypes=filetypes,
                initialdir=initial_dir
            )
        else:
            # For Linux/Mac, let's select the directory instead
            file_path = filedialog.askdirectory(
                title="Select ITGMania Directory",
                initialdir=initial_dir
            )
        
        if file_path:
            self.path_var.set(file_path)
            
            # Try to find the Simply Love theme and auto-fill the image path
            if self.use_default_image_var.get():
                itg_dir = os.path.dirname(file_path)
                if self.app.install_manager.is_windows:
                    # For Windows, the exe is in the root dir
                    theme_dir = os.path.join(itg_dir, "Themes", "Simply Love")
                else:
                    # For Linux/Mac, find the appropriate path
                    theme_dir = os.path.join(file_path, "Themes", "Simply Love")
                
                default_image = os.path.join(theme_dir, "Graphics", "Banner.png")
                if os.path.isfile(default_image):
                    self.default_image_path = default_image
    
    def browse_image(self):
        """Open a file browser dialog for selecting the ITGMania banner image."""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("All files", "*.*")
        ]
        
        image_path = filedialog.askopenfilename(
            title="Select ITGMania Banner Image",
            filetypes=filetypes
        )
        
        if image_path:
            self.image_var.set(image_path)
    
    def validate(self):
        """Validate ITGMania settings."""
        if not self.use_itgmania_var.get():
            return True
        
        # Validate ITGMania path
        itgmania_path = self.path_var.get().strip()
        if not itgmania_path:
            messagebox.showerror(
                "Invalid Path", 
                "Please enter the path to ITGMania."
            )
            return False
        
        # Check if the path exists
        if not os.path.exists(itgmania_path):
            messagebox.showerror(
                "Invalid Path", 
                "The specified ITGMania path does not exist."
            )
            return False
        
        # For Windows, check if it's an executable
        if self.app.install_manager.is_windows and not itgmania_path.lower().endswith(".exe"):
            messagebox.showerror(
                "Invalid Path", 
                "Please select the ITGMania executable (.exe) file."
            )
            return False
        
        # Validate image path if custom image is selected
        if not self.use_default_image_var.get():
            image_path = self.image_var.get().strip()
            if image_path and not os.path.isfile(image_path):
                messagebox.showerror(
                    "Invalid Image", 
                    "The specified banner image file does not exist."
                )
                return False
        
        return True
    
    def save_data(self):
        """Save ITGMania settings."""
        self.app.user_config["use_itgmania"] = self.use_itgmania_var.get()
        
        if self.use_itgmania_var.get():
            self.app.user_config["itgmania_path"] = self.path_var.get().strip()
            
            if self.use_default_image_var.get():
                # Use default Simply Love image
                itg_dir = os.path.dirname(self.path_var.get().strip())
                if self.app.install_manager.is_windows:
                    theme_dir = os.path.join(itg_dir, "Themes", "Simply Love")
                else:
                    theme_dir = os.path.join(self.path_var.get().strip(), "Themes", "Simply Love")
                
                default_image = os.path.join(theme_dir, "Graphics", "Banner.png")
                if os.path.isfile(default_image):
                    self.app.user_config["itgmania_image"] = default_image
                elif self.default_image_path and os.path.isfile(self.default_image_path):
                    self.app.user_config["itgmania_image"] = self.default_image_path
            else:
                # Use custom image
                self.app.user_config["itgmania_image"] = self.image_var.get().strip()
            
            self.app.user_config["install_itgmania_module"] = self.install_module_var.get() 