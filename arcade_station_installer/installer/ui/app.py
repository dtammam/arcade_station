"""
Main application class for the Arcade Station Installer
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox

from ..config.installation import InstallationManager
from .pages import (
    WelcomePage,
    InstallLocationPage,
    KioskModePage,
    DisplayConfigPage,
    GameSetupPage,
    ITGManiaSetupPage,
    BinaryGamesPage,
    MAMEGamesPage,
    ControlConfigPage,
    LightsConfigPage,
    UtilityConfigPage,
    SummaryPage,
)

class InstallerApp:
    """Main application class for the Arcade Station Installer."""
    
    def __init__(self, root):
        """Initialize the application.
        
        Args:
            root: The tkinter root window
        """
        self.root = root
        self.root.title("Arcade Station Installer")
        
        # State management for wizard
        self.current_page = 0
        self.pages = []
        self.user_config = {}
        
        # Installation manager
        self.install_manager = InstallationManager()
        
        # Check if already installed
        self.is_installed = self.install_manager.check_if_installed()
        self.is_reset_mode = False
        self.is_reconfigure_mode = False
        
        # Setup wizard framework
        self.container = ttk.Frame(root)
        self.container.pack(fill="both", expand=True)
        
        # Create sidebar for navigation
        self.setup_sidebar()
        
        # Create the pages
        self.setup_pages()
        
        # Show the first page
        self.show_page(0)
        
        # Set window size and center it
        window_width = 1000
        window_height = 1000
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        root.minsize(window_width, window_height)
        
        # Make sure the window is on top (but not always-on-top)
        root.attributes('-topmost', True)
        root.update()
        root.attributes('-topmost', False)
    
    def setup_sidebar(self):
        """Create the sidebar with progress indicators."""
        self.sidebar = ttk.Frame(self.container, width=200, style="Sidebar.TFrame")
        self.sidebar.pack(fill="y", side="left", padx=0, pady=0)
        
        # Make the sidebar have a different background
        style = ttk.Style()
        style.configure("Sidebar.TFrame", background="#2c3e50")
        
        # Add logo at the top
        logo_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        logo_frame.pack(fill="x", padx=10, pady=20)
        
        logo_label = ttk.Label(logo_frame, text="Arcade Station", 
                             foreground="white", background="#2c3e50",
                             font=("Arial", 16, "bold"))
        logo_label.pack(anchor="center")
        
        # Create frame for step indicators
        self.steps_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        self.steps_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Step indicators will be added when pages are created
        self.step_labels = []
    
    def add_step_indicator(self, text):
        """Add a step indicator to the sidebar.
        
        Args:
            text: The text to display for this step
        """
        index = len(self.step_labels)
        step_frame = ttk.Frame(self.steps_frame, style="Sidebar.TFrame")
        step_frame.pack(fill="x", padx=5, pady=2, anchor="w")
        
        # Create the step number indicator
        indicator = ttk.Label(step_frame, text=f"{index + 1}", 
                            width=2, anchor="center",
                            foreground="white", background="#7f8c8d",
                            font=("Arial", 9))
        indicator.pack(side="left", padx=(0, 10))
        
        # Create the step text
        label = ttk.Label(step_frame, text=text, 
                        foreground="#bdc3c7", background="#2c3e50",
                        font=("Arial", 10))
        label.pack(side="left", fill="x", expand=True)
        
        self.step_labels.append((indicator, label))
        
    def update_step_indicators(self):
        """Update the styling of step indicators based on current page."""
        for i, (indicator, label) in enumerate(self.step_labels):
            if i < self.current_page:
                # Completed steps
                indicator.configure(background="#27ae60", foreground="white")
                label.configure(foreground="white")
            elif i == self.current_page:
                # Current step
                indicator.configure(background="#3498db", foreground="white")
                label.configure(foreground="white", font=("Arial", 10, "bold"))
            else:
                # Future steps
                indicator.configure(background="#7f8c8d", foreground="white")
                label.configure(foreground="#bdc3c7", font=("Arial", 10))
    
    def setup_pages(self):
        """Create all wizard pages."""
        # Content frame
        self.content = ttk.Frame(self.container)
        self.content.pack(fill="both", expand=True, side="right", padx=0, pady=0)
        
        # Create the different pages
        self.pages = [
            WelcomePage(self.content, self),
            InstallLocationPage(self.content, self),
        ]
        
        # Conditionally add pages based on platform and installation state
        self.conditional_pages = {
            "kiosk": KioskModePage(self.content, self),
            "display": DisplayConfigPage(self.content, self),
            "game_setup": GameSetupPage(self.content, self),
            "itgmania": ITGManiaSetupPage(self.content, self),
            "binary_games": BinaryGamesPage(self.content, self),
            "mame_games": MAMEGamesPage(self.content, self),
            "control_config": ControlConfigPage(self.content, self),
            "lights": LightsConfigPage(self.content, self),
            "utility": UtilityConfigPage(self.content, self),
            "summary": SummaryPage(self.content, self),
        }
        
        # Add step indicators for initial pages
        self.add_step_indicator("Welcome")
        self.add_step_indicator("Install Location")
        
        # The rest of the step indicators will be added dynamically
        # based on the user's choices and platform
    
    def decide_next_page_flow(self):
        """Determine which pages to include based on user choices."""
        # If in reset mode or reconfigure mode, load existing config
        if self.is_installed and (self.is_reset_mode or self.is_reconfigure_mode):
            # Load existing configuration to pre-populate fields
            existing_install_path = self.install_manager.get_current_install_path()
            self.user_config["install_path"] = existing_install_path
            
            # Load existing configuration files
            if self.is_reconfigure_mode:
                self._load_existing_config(existing_install_path)
        
        # Determine which pages to show based on the OS and options
        page_flow = [0]  # Always start with welcome page
        
        # Always include installation location
        page_flow.append(1)
        
        # Windows-specific pages
        if self.install_manager.is_windows:
            # Kiosk mode (Windows only)
            page_flow.append("kiosk")
        
        # Display configuration
        page_flow.append("display")
        
        # Game setup pages
        page_flow.append("game_setup")
        page_flow.append("itgmania")
        page_flow.append("binary_games")
        page_flow.append("mame_games")
        
        # Control configuration
        page_flow.append("control_config")
        
        # Lights configuration
        page_flow.append("lights")
        
        # Utility configuration (VPN, streaming)
        page_flow.append("utility")
        
        # Summary page (always last)
        page_flow.append("summary")
        
        # IMPORTANT: Actually rebuild the pages list based on page_flow
        # Keep the first two pages (welcome and install location)
        new_pages = self.pages[:2]
        
        # Add the conditional pages based on our flow
        for idx in page_flow[2:]:  # Skip the first two which are already in new_pages
            if isinstance(idx, str):
                # Add this conditional page to our sequence
                new_pages.append(self.conditional_pages[idx])
                
                # Add step indicator if it doesn't exist yet
                if len(self.step_labels) <= len(new_pages) - 1:
                    page_name = idx.replace("_", " ").title()
                    self.add_step_indicator(page_name)
        
        # Update the pages list
        self.pages = new_pages
        
        # Update step indicators
        self.update_step_indicators()
    
    def _load_existing_config(self, install_path):
        """Load existing configuration files to pre-populate the UI.
        
        Args:
            install_path: Path to the existing installation
        """
        import os
        import tomli
        
        config_dir = os.path.join(install_path, "config")
        
        # Try to load various configuration files
        config_files = {
            "display_config": "display_config.toml",
            "key_listener": "key_listener.toml",
            "installed_games": "installed_games.toml",
            "processes_to_kill": "processes_to_kill.toml",
            "utility_config": "utility_config.toml",
            "mame_config": "mame_config.toml",
        }
        
        for config_key, filename in config_files.items():
            filepath = os.path.join(config_dir, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, "rb") as f:
                        config_data = tomli.load(f)
                    self.user_config[config_key] = config_data
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        # Check Windows registry for kiosk settings if on Windows
        if self.install_manager.is_windows and self.is_reconfigure_mode:
            try:
                import winreg
                reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
                
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, 
                                   winreg.KEY_READ) as key:
                    try:
                        value, _ = winreg.QueryValueEx(key, "DefaultUserName")
                        self.user_config["kiosk_username"] = value
                    except:
                        pass
                    
                    try:
                        value, _ = winreg.QueryValueEx(key, "AutoAdminLogon")
                        self.user_config["enable_kiosk_mode"] = (value == "1")
                    except:
                        pass
                    
                    try:
                        value, _ = winreg.QueryValueEx(key, "Shell")
                        self.user_config["kiosk_replace_shell"] = (value != "explorer.exe")
                    except:
                        pass
            except:
                pass
    
    def next_page(self):
        """Advance to the next page in the wizard."""
        if self.current_page < len(self.pages) - 1:
            self.show_page(self.current_page + 1)
        else:
            # We've reached the end of the wizard
            self.finish_installation()
    
    def prev_page(self):
        """Go back to the previous page in the wizard."""
        if self.current_page > 0:
            self.show_page(self.current_page - 1)
    
    def show_page(self, index):
        """Show the specified page and update navigation.
        
        Args:
            index: The index of the page to show
        """
        # Hide current page
        if 0 <= self.current_page < len(self.pages):
            self.pages[self.current_page].hide()
        
        # Update current page index
        self.current_page = index
        
        # Show the new page
        self.pages[index].show()
        
        # Update step indicators
        self.update_step_indicators()
    
    def finish_installation(self):
        """Complete the installation process."""
        try:
            # Show a busy cursor
            self.root.config(cursor="wait")
            self.root.update()
            
            # Perform the installation
            success = self.install_manager.perform_installation(self.user_config)
            
            # Restore cursor
            self.root.config(cursor="")
            
            if success:
                messagebox.showinfo(
                    "Installation Complete", 
                    "Arcade Station has been successfully installed!"
                )
                self.root.destroy()
            else:
                messagebox.showerror(
                    "Installation Failed", 
                    "There was a problem during installation. Please check the logs."
                )
        except Exception as e:
            self.root.config(cursor="")
            messagebox.showerror(
                "Error", 
                f"An unexpected error occurred: {str(e)}"
            )
    
    def set_reset_mode(self, reset_mode=True):
        """Set whether the installer is in reset mode.
        
        Args:
            reset_mode: True for reset mode, False for normal installation
        """
        self.is_reset_mode = reset_mode
        
        # Reconfigure page flow based on reset mode
        self.decide_next_page_flow() 