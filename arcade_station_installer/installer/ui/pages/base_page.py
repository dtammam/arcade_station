"""
Base Page class for all installer wizard pages
"""
import tkinter as tk
from tkinter import ttk

class BasePage:
    """Base class for all installer wizard pages."""
    
    def __init__(self, container, app):
        """Initialize the base page.
        
        Args:
            container: The parent container (frame)
            app: The main application instance for accessing shared state
        """
        self.container = container
        self.app = app
        self.frame = ttk.Frame(container)
        
        # Common elements
        self.header_frame = ttk.Frame(self.frame)
        self.header_frame.pack(fill="x", padx=10, pady=(20, 10))
        
        self.title_label = ttk.Label(self.header_frame, style="Title.TLabel")
        self.title_label.pack(anchor="w")
        
        self.subtitle_label = ttk.Label(self.header_frame, style="Heading.TLabel")
        self.subtitle_label.pack(anchor="w", pady=(5, 0))
        
        # Content area
        self.content_frame = ttk.Frame(self.frame)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Button area at bottom
        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.pack(fill="x", side="bottom", padx=10, pady=10)
        
        self.back_button = ttk.Button(self.button_frame, text="Back", command=self.on_back)
        self.back_button.pack(side="left", padx=5, pady=5)
        
        self.next_button = ttk.Button(self.button_frame, text="Next", command=self.on_next)
        self.next_button.pack(side="right", padx=5, pady=5)
        
        # Create page-specific widgets
        self.create_widgets()
    
    def create_widgets(self):
        """Create page-specific widgets.
        
        Override in subclasses to add page-specific content.
        """
        pass
    
    def on_enter(self):
        """Called when the page is shown.
        
        Override in subclasses for page-specific initialization.
        """
        pass
    
    def on_leave(self):
        """Called when leaving the page.
        
        Override in subclasses for page-specific cleanup.
        """
        pass
    
    def on_next(self):
        """Handle next button click.
        
        Validates and saves data, then advances to the next page.
        """
        if self.validate():
            self.save_data()
            self.on_leave()
            self.app.next_page()
    
    def on_back(self):
        """Handle back button click."""
        self.on_leave()
        self.app.prev_page()
    
    def validate(self):
        """Validate the page data before proceeding.
        
        Returns:
            bool: True if validation passes, False otherwise
        """
        return True
    
    def save_data(self):
        """Save the data from this page to the app's user_config.
        
        Override in subclasses to save page-specific data.
        """
        pass
    
    def show(self):
        """Show this page."""
        self.frame.pack(fill="both", expand=True)
        self.on_enter()
    
    def hide(self):
        """Hide this page."""
        self.frame.pack_forget()
    
    def set_title(self, title, subtitle=""):
        """Set the page title and subtitle.
        
        Args:
            title: The main title text
            subtitle: The subtitle text
        """
        self.title_label.config(text=title)
        self.subtitle_label.config(text=subtitle)
        
    def set_next_button_text(self, text):
        """Change the text of the next button.
        
        Args:
            text: The new button text
        """
        self.next_button.config(text=text)
        
    def set_back_button_state(self, enabled=True):
        """Enable or disable the back button.
        
        Args:
            enabled: True to enable, False to disable
        """
        self.back_button.config(state="normal" if enabled else "disabled")
        
    def set_next_button_state(self, enabled=True):
        """Enable or disable the next button.
        
        Args:
            enabled: True to enable, False to disable
        """
        self.next_button.config(state="normal" if enabled else "disabled") 