"""
ITGMania setup page for the Arcade Station Installer
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import platform
import tomllib
import logging

from .base_page import BasePage

class ITGManiaSetupPage(BasePage):
    """Page for setting up ITGMania integration."""
    
    def __init__(self, container, app):
        """Initialize the ITGMania setup page."""
        # Initialize variables before parent's __init__
        self.default_image_path = ""
        self.default_paths = {
            "Windows": r"C:\Games\ITGmania\Program\ITGmania.exe",
            "Linux": "/opt/itgmania/Program/ITGmania",
            "Darwin": "/Applications/ITGmania/Program/ITGmania.app/Contents/MacOS/ITGmania"
        }
        self.current_os = platform.system()
        self.default_itgmania_path = self.default_paths.get(self.current_os, "")
        
        # Call parent's __init__ which will call create_widgets
        super().__init__(container, app)
        
        # Set title and default image path after parent initialization
        self.set_title(
            "ITGMania Setup",
            "Configure ITGMania integration"
        )
        
        if "install_path" in self.app.user_config:
            asset_path = os.path.join(
                self.app.user_config["install_path"],
                "assets", "images", "banners", "itgmania.png"
            )
            self.default_image_path = asset_path
            # Update the image path if using default
            if self.use_default_image_var.get():
                self.image_var.set(asset_path)
        
        # Initialize UI state after all variables are set
        self.toggle_default_image()
    
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
            # Set the default image path and disable the entry
            if self.default_image_path:
                self.image_var.set(self.default_image_path)
            self.image_entry.config(state="disabled")
            self.browse_image_button.config(state="disabled")
        else:
            self.image_entry.config(state="normal")
            self.browse_image_button.config(state="normal")
            self.image_var.set("")
    
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
        # Load existing ITGMania config if in reconfigure mode
        if hasattr(self.app, 'is_reconfigure_mode') and self.app.is_reconfigure_mode:
            installed_games_path = os.path.join(self.app.user_config.get("install_path", ""), "config", "installed_games.toml")
            if os.path.exists(installed_games_path):
                try:
                    with open(installed_games_path, "rb") as f:
                        installed_games = tomllib.load(f)
                        if "games" in installed_games and "itgmania" in installed_games["games"]:
                            itgmania_config = installed_games["games"]["itgmania"]
                            
                            # Enable ITGMania checkbox
                            self.use_itgmania_var.set(True)
                            
                            # Set path
                            if "path" in itgmania_config:
                                self.path_var.set(itgmania_config["path"])
                                # If the path matches the default, check the default path checkbox
                                if itgmania_config["path"] == self.default_itgmania_path:
                                    self.use_default_path_var.set(True)
                                    self.default_path_checkbox.pack(anchor="w", pady=(0, 5))
                                    self.toggle_default_path()
                            
                            # Set banner image
                            if "banner" in itgmania_config:
                                self.image_var.set(itgmania_config["banner"])
                                
                                # Check if the banner path is the default by checking if it ends with the default relative path
                                banner_path = itgmania_config["banner"]
                                default_relative_path = os.path.join("assets", "images", "banners", "itgmania.png")
                                
                                # Normalize both paths to handle different slash styles
                                banner_path = os.path.normpath(banner_path)
                                default_relative_path = os.path.normpath(default_relative_path)
                                
                                # Check if the banner path ends with the default relative path
                                if banner_path.lower().endswith(default_relative_path.lower()):
                                    self.use_default_image_var.set(True)
                                else:
                                    self.use_default_image_var.set(False)
                            
                            # Set module installation
                            if "display_module_installed" in itgmania_config:
                                self.install_module_var.set(itgmania_config["display_module_installed"])
                            
                            # Update UI state
                            self.toggle_itgmania_settings()
                            self.toggle_default_image()
                except Exception as e:
                    logging.warning(f"Failed to load existing ITGMania config: {e}")
        
        # Update the default image path based on the current installation path
        if "install_path" in self.app.user_config:
            asset_path = os.path.join(
                self.app.user_config["install_path"],
                "assets", "images", "banners", "itgmania.png"
            )
            self.default_image_path = asset_path
            # If using default image, update the path display
            if self.use_default_image_var.get():
                self.image_var.set(asset_path)
        
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
                        "assets", "images", "banners", "itgmania.png"
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
            
            # Add ITGMania to installed games in the correct format
            self.app.user_config["installed_games"]["games"]["itgmania"] = {
                "path": itgmania_path,
                "banner": image_path
            }
            
            # IMPORTANT: Also add to binary_games which is used for metadata.pegasus.txt generation
            if "binary_games" not in self.app.user_config:
                self.app.user_config["binary_games"] = {}
                
            # Add ITGMania to binary games with the same format
            self.app.user_config["binary_games"]["itgmania"] = {
                "path": itgmania_path,
                "banner": image_path
            }
            
            # Check if we should run the ITGMania setup script
            if self.use_itgmania_var.get() and self.install_module_var.get():
                try:
                    # Import and use the setup module directly
                    import sys
                    import logging
                    from pathlib import Path
                    
                    # Import the setup function using an absolute import path that will work with the installer structure
                    from installer.resources.itgmania_integration.itgmania_dynamic_marquee_setup import setup_itgmania_integration
                    
                    # Get the ITGMania installation path from the UI
                    itgmania_path = self.path_var.get().strip()
                    
                    # Get the banner image path if using custom image
                    banner_path = None
                    if not self.use_default_image_var.get() and self.image_var.get().strip():
                        banner_path = self.image_var.get().strip()
                    
                    # Call the setup function directly
                    logging.info(f"Setting up ITGMania integration with path: {itgmania_path}")
                    logging.info(f"Using banner path: {banner_path}")
                    
                    # First clear any existing configuration to force update
                    try:
                        # Try to access and modify the config file directly
                        config_path = os.path.join(self.app.user_config["install_path"], "config", "display_config.toml")
                        if os.path.exists(config_path):
                            logging.info(f"Found config file at: {config_path}, clearing ITGMania path")
                            
                            # Check if we need to use tomli_w or manual writing
                            try:
                                import tomli_w
                                
                                # Read existing config
                                with open(config_path, "rb") as f:
                                    config = tomllib.load(f)
                                
                                # Clear the existing path
                                if "dynamic_marquee" in config:
                                    if "itgmania_display_file_path" in config["dynamic_marquee"]:
                                        config["dynamic_marquee"]["itgmania_display_file_path"] = ""
                                        logging.info("Cleared the existing ITGMania display file path")
                                
                                # Write back
                                with open(config_path, "wb") as f:
                                    tomli_w.dump(config, f)
                            except ImportError:
                                logging.info("tomli_w not available, will rely on setup script")
                    except Exception as e:
                        logging.error(f"Error clearing config: {e}")
                    
                    # Run the setup
                    success = setup_itgmania_integration(itgmania_path, banner_path)
                    
                    if not success:
                        logging.error("ITGMania integration setup failed")
                    else:
                        logging.info("ITGMania integration setup completed successfully")
                        
                        # Verify the configuration was updated
                        try:
                            config_path = os.path.join(self.app.user_config["install_path"], "config", "display_config.toml")
                            if os.path.exists(config_path):
                                with open(config_path, "rb") as f:
                                    config = tomllib.load(f)
                                
                                if "dynamic_marquee" in config and "itgmania_display_file_path" in config["dynamic_marquee"]:
                                    path = config["dynamic_marquee"]["itgmania_display_file_path"]
                                    logging.info(f"Verified config - itgmania_display_file_path: {path}")
                                else:
                                    logging.error("itgmania_display_file_path not found in config after setup!")
                        except Exception as e:
                            logging.error(f"Error verifying config: {e}")
                    
                except Exception as e:
                    logging.error(f"Failed to run ITGMania setup script: {e}")