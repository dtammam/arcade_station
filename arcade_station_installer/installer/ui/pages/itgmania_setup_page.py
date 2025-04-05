"""
ITGMania setup page for the Arcade Station Installer
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import platform

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
        
        # Set default paths based on OS
        self.default_paths = {
            "Windows": r"C:\Games\ITGmania\Program\ITGmania.exe",
            "Linux": "/opt/itgmania/Program/ITGmania",
            "Darwin": "/Applications/ITGmania/Program/ITGmania.app/Contents/MacOS/ITGmania"
        }
        self.current_os = platform.system()
        self.default_itgmania_path = self.default_paths.get(self.current_os, "")
        
        # Set the default image path to the standard asset location
        if "install_path" in self.app.user_config:
            asset_path = os.path.join(
                self.app.user_config["install_path"],
                "assets", "images", "banners", "simply-love.png"
            )
            self.default_image_path = asset_path
    
    def create_widgets(self):
        """Create page-specific widgets."""
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Introduction
        intro_text = ttk.Label(
            main_frame,
            text="ITGMania is a popular dance game simulator. Arcade Station can integrate "
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
        self.path_entry = ttk.Entry(
            path_frame,
            textvariable=self.path_var,
            width=40
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.browse_button = ttk.Button(
            path_frame,
            text="Browse...",
            command=self.browse_itgmania
        )
        self.browse_button.pack(side="right")
        
        # Default path detection checkbox
        self.use_default_path_var = tk.BooleanVar(value=False)
        self.default_path_checkbox = ttk.Checkbutton(
            self.itgmania_frame,
            text="Default installation path detected, uncheck if you'd like to set to something else.",
            variable=self.use_default_path_var,
            command=self.toggle_default_path
        )
        
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
    
    def toggle_default_path(self):
        """Enable or disable the path entry based on default path checkbox."""
        if self.use_default_path_var.get():
            self.path_var.set(self.default_itgmania_path)
            self.path_entry.config(state="disabled")
            self.browse_button.config(state="disabled")
        else:
            self.path_entry.config(state="normal")
            self.browse_button.config(state="normal")
            self.path_var.set("")
    
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
                "ITGMania Path Required", 
                "Please specify the path to the ITGMania executable or directory."
            )
            return False
        
        if not os.path.exists(itgmania_path):
            messagebox.showerror(
                "Invalid ITGMania Path", 
                "The specified ITGMania path does not exist."
            )
            return False
        
        # Validate image path if not using default
        if not self.use_default_image_var.get():
            image_path = self.image_var.get().strip()
            if image_path and not os.path.isfile(image_path):
                messagebox.showerror(
                    "Invalid Image", 
                    "The specified image file does not exist."
                )
                return False
        
        return True
    
    def on_enter(self):
        """Called when the page is shown."""
        # Update the default image path based on the current installation path
        if "install_path" in self.app.user_config:
            asset_path = os.path.join(
                self.app.user_config["install_path"],
                "assets", "images", "banners", "simply-love.png"
            )
            self.default_image_path = asset_path
        
        # Check for default ITGMania path based on OS
        if os.path.exists(self.default_itgmania_path):
            self.use_default_path_var.set(True)
            self.path_var.set(self.default_itgmania_path)
            self.default_path_checkbox.pack(anchor="w", pady=(0, 5))
            self.toggle_default_path()
        else:
            self.use_default_path_var.set(False)
            self.default_path_checkbox.pack_forget()
            self.path_var.set("")
        
        # Pre-populate fields if in reconfiguration mode
        if hasattr(self.app, 'is_reconfigure_mode') and self.app.is_reconfigure_mode:
            if 'installed_games' in self.app.user_config:
                # Check if ITGMania is in installed games
                installed_games = self.app.user_config['installed_games']
                if 'games' in installed_games and 'itgmania' in installed_games['games']:
                    itgmania_config = installed_games['games']['itgmania']
                    
                    # Enable ITGMania checkbox
                    self.use_itgmania_var.set(True)
                    
                    # Set path
                    if 'path' in itgmania_config:
                        self.path_var.set(itgmania_config['path'])
                        # If the path matches the default, check the default path checkbox
                        if itgmania_config['path'] == self.default_itgmania_path:
                            self.use_default_path_var.set(True)
                            self.default_path_checkbox.pack(anchor="w", pady=(0, 5))
                            self.toggle_default_path()
                    
                    # Set banner image
                    if 'banner' in itgmania_config:
                        self.use_default_image_var.set(False)
                        self.image_var.set(itgmania_config['banner'])
                    
                    # Set module installation
                    if 'display_module_installed' in itgmania_config:
                        self.install_module_var.set(itgmania_config['display_module_installed'])
                    
                    # Update UI state
                    self.toggle_itgmania_settings()
                    self.toggle_default_image()

    def save_data(self):
        """Save ITGMania settings."""
        self.app.user_config["itgmania"] = {
            "enabled": self.use_itgmania_var.get()
        }
        
        if self.use_itgmania_var.get():
            # Store basic ITGMania config for internal use
            itgmania_path = self.path_var.get().strip()
            self.app.user_config["itgmania"].update({
                "path": itgmania_path,
                "use_default_image": self.use_default_image_var.get(),
                "install_marquee_module": self.install_module_var.get()
            })
            
            # Determine which image to use
            image_path = ""
            if self.use_default_image_var.get():
                # Make sure we're using the asset in the installation directory
                if "install_path" in self.app.user_config:
                    # Define the path to the Simply Love banner in the assets directory
                    asset_path = os.path.join(
                        self.app.user_config["install_path"],
                        "assets", "images", "banners", "simply-love.png"
                    )
                    image_path = asset_path
                    self.app.user_config["itgmania"]["default_image_path"] = asset_path
                    
                    # Make sure the directory exists
                    asset_dir = os.path.dirname(asset_path)
                    os.makedirs(asset_dir, exist_ok=True)
                    
                    # If the default image doesn't exist yet, create an empty file 
                    # (it will be properly copied during the installation process)
                    if not os.path.exists(asset_path):
                        try:
                            with open(asset_path, 'w') as f:
                                f.write("")
                        except:
                            pass
            elif not self.use_default_image_var.get() and self.image_var.get().strip():
                custom_path = self.image_var.get().strip()
                image_path = custom_path
                self.app.user_config["itgmania"]["custom_image"] = custom_path
                
                # If custom image is selected, copy it to the assets directory for future use
                if "install_path" in self.app.user_config and os.path.exists(custom_path):
                    try:
                        # Extract filename and create destination path
                        filename = os.path.basename(custom_path)
                        dest_path = os.path.join(
                            self.app.user_config["install_path"],
                            "assets", "images", "banners", filename
                        )
                        
                        # Create directory if needed
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        
                        # Copy the file if it's not already in the assets directory
                        if custom_path != dest_path and not os.path.exists(dest_path):
                            import shutil
                            shutil.copy2(custom_path, dest_path)
                            
                            # Update the path to point to the copied file
                            image_path = dest_path
                            self.app.user_config["itgmania"]["custom_image"] = dest_path
                    except Exception as e:
                        print(f"Error copying custom image: {str(e)}")
            
            # Create/update installed_games.toml structure
            if "installed_games" not in self.app.user_config:
                self.app.user_config["installed_games"] = {"games": {}}
            
            # Add ITGMania to installed games
            self.app.user_config["installed_games"]["games"]["itgmania"] = {
                "display_name": "ITGMania",
                "path": itgmania_path,
                "type": "binary",
                "launch_args": "",
                "banner": image_path,
                "enabled": True
            }
            
            # IMPORTANT: Also add to binary_games which is used for metadata.pegasus.txt generation
            if "binary_games" not in self.app.user_config:
                self.app.user_config["binary_games"] = {}
                
            # Add ITGMania to binary games with the same format as other binary games
            self.app.user_config["binary_games"]["itgmania"] = {
                "id": "itgmania",
                "display_name": "ITGMania",
                "path": itgmania_path,
                "banner": image_path
            } 