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
        
        # Setup wizard framework
        self.container = ttk.Frame(root)
        self.container.pack(fill="both", expand=True)
        
        # Create sidebar with progress indicators
        self.setup_sidebar()
        
        # Create pages
        self.setup_pages()
        
        # Show first page
        self.show_page(0)
    
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
        """Decide which pages to include in the wizard based on user choices.
        
        This is called when transitioning from the welcome page.
        """
        # Reset current page flow
        self.pages = self.pages[:2]  # Keep welcome and install location pages
        
        # Add steps based on installation state and platform
        next_pages = []
        
        # Add kiosk mode page for Windows
        if self.install_manager.is_windows and not self.is_reset_mode:
            next_pages.append(("kiosk", "Kiosk Mode"))
        
        # Add display config page
        next_pages.append(("display", "Display Configuration"))
        
        # Add game setup pages
        next_pages.append(("game_setup", "Game Setup"))
        
        # These game pages may be skipped based on user choice in GameSetupPage
        next_pages.append(("itgmania", "ITGMania Setup"))
        next_pages.append(("binary_games", "Binary Games"))
        next_pages.append(("mame_games", "MAME Games"))
        
        # Add control config page
        next_pages.append(("control_config", "Control Configuration"))
        
        # Add lights configuration page
        next_pages.append(("lights", "Lighting Setup"))
        
        # Add utility configuration page
        next_pages.append(("utility", "Utility Options"))
        
        # Add summary page
        next_pages.append(("summary", "Summary & Install"))
        
        # Add pages to the flow
        for page_key, step_name in next_pages:
            if page_key in self.conditional_pages:
                self.pages.append(self.conditional_pages[page_key])
                # Only add step indicator if it doesn't already exist
                if len(self.step_labels) <= len(self.pages) - 1:
                    self.add_step_indicator(step_name)
        
        # Update step indicators
        self.update_step_indicators()
    
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