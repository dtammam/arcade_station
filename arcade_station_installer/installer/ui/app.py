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
        
        # Initialize installation status - will be checked later
        self.is_installed = False
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
        # Create temporary list of pages to include
        new_page_flow = []
        
        # Always include welcome and installation location pages
        new_page_flow.append(self.pages[0] if len(self.pages) > 0 else WelcomePage(self.content, self))
        new_page_flow.append(self.pages[1] if len(self.pages) > 1 else InstallLocationPage(self.content, self))
        
        # Clear step indicators and recreate them
        for indicator, label in self.step_labels:
            indicator.destroy()
            label.destroy()
        self.step_labels = []
        
        # Add step indicators for initial pages
        self.add_step_indicator("Welcome")
        self.add_step_indicator("Install Location")
        
        # Determine which conditional pages to include
        if not self.is_reconfigure_mode or self.user_config.get("reconfigure_games", True):
            # Game setup pages
            new_page_flow.append(self.conditional_pages["game_setup"])
            self.add_step_indicator("Game Setup")
            
            # Only include game pages if not skipping game configuration
            if not self.user_config.get("skip_games", False):
                new_page_flow.append(self.conditional_pages["itgmania"])
                new_page_flow.append(self.conditional_pages["binary_games"])
                new_page_flow.append(self.conditional_pages["mame_games"])
                self.add_step_indicator("ITGMania Setup")
                self.add_step_indicator("Binary Games")
                self.add_step_indicator("MAME Games")
        
        # Always include these configuration pages
        new_page_flow.append(self.conditional_pages["control_config"])
        new_page_flow.append(self.conditional_pages["display"])
        self.add_step_indicator("Control Config")
        self.add_step_indicator("Display Config")
        
        # Include Windows-specific kiosk mode page
        if self.install_manager.is_windows:
            new_page_flow.append(self.conditional_pages["kiosk"])
            self.add_step_indicator("Kiosk Mode")
        
        # Optional pages based on user choices
        if not self.is_reconfigure_mode or self.user_config.get("reconfigure_utilities", True):
            new_page_flow.append(self.conditional_pages["utility"])
            self.add_step_indicator("Utilities")
        
        # Always include summary page
        new_page_flow.append(self.conditional_pages["summary"])
        self.add_step_indicator("Summary")
        
        # Update the pages list - hide all current pages first
        for page in self.pages:
            page.hide()
            
        # Set the new page flow
        self.pages = new_page_flow
        
        # Debug: print page count and names
        page_names = [page.__class__.__name__ for page in self.pages]
        print(f"Wizard flow: {len(self.pages)} pages - {', '.join(page_names)}")
        
        # Make sure we update the current page's back button if it's the welcome page
        if self.current_page == 0 and isinstance(self.pages[0], WelcomePage):
            self.pages[0].set_back_button_state(False)
            
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

    def check_installation_status(self):
        """Check if Arcade Station is already installed at the selected location."""
        if "install_path" in self.user_config and self.user_config["install_path"]:
            # Check if installation exists at the selected path
            install_path = self.user_config["install_path"]
            self.is_installed = self.install_manager.check_if_installed_at_path(install_path)
            
            # If installation is found and we're in reconfigure mode, load existing config
            if self.is_installed and self.is_reconfigure_mode:
                self._load_existing_config(install_path)
                
            return self.is_installed
        return False 