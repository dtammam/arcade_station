"""
Base Wizard Module for Arcade Station Installer.

This module provides the foundation for the installer wizard UI,
handling navigation between pages and common functionality.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk
import threading
import logging
from pathlib import Path

# Import CustomTkinter if available, otherwise use standard ttk styling
try:
    import customtkinter as ctk
    USE_CTK = True
except ImportError:
    USE_CTK = False
    
# Import core functions
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.core_functions import determine_operating_system, is_admin, logger

class BaseWizardApp:
    """
    Base class for the Arcade Station installer wizard.
    
    This class provides the common functionality for both the
    initial setup wizard and the update wizard.
    """
    
    def __init__(self, title="Arcade Station Installer", width=800, height=600, theme="dark"):
        """
        Initialize the wizard application.
        
        Args:
            title (str): Window title.
            width (int): Window width.
            height (int): Window height.
            theme (str): UI theme ("dark" or "light").
        """
        self.title = title
        self.width = width
        self.height = height
        self.theme = theme
        
        # Store configuration data from wizard pages
        self.config_data = {}
        
        # Create the main window
        if USE_CTK:
            # Set appearance mode and color theme
            ctk.set_appearance_mode(theme)
            ctk.set_default_color_theme("blue")
            
            # Create CTk root window
            self.root = ctk.CTk()
        else:
            # Use standard Tkinter with styling
            self.root = tk.Tk()
            self.style = ttk.Style()
            if theme == "dark":
                # Apply dark theme with ttk
                self.root.configure(bg="#2b2b2b")
                self.style.configure("TFrame", background="#2b2b2b")
                self.style.configure("TLabel", background="#2b2b2b", foreground="white")
                self.style.configure("TButton", background="#3d3d3d", foreground="white")
            else:
                # Apply light theme with ttk
                self.root.configure(bg="#f0f0f0")
                self.style.configure("TFrame", background="#f0f0f0")
                self.style.configure("TLabel", background="#f0f0f0", foreground="black")
                self.style.configure("TButton", background="#e0e0e0", foreground="black")
        
        # Configure the window
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(False, False)
        
        # Set window icon if available
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'assets', 'images', 'arcade_station_icon.ico'))
        if os.path.exists(icon_path):
            try:
                if sys.platform == 'win32':
                    self.root.iconbitmap(icon_path)
                else:
                    # For Linux/Mac
                    icon_img = tk.PhotoImage(file=icon_path)
                    self.root.iconphoto(True, icon_img)
            except Exception as e:
                logger.warning(f"Could not set window icon: {e}")
        
        # Variables to track wizard state
        self.current_page = None
        self.pages = {}
        self.page_order = []
        self.system_info = self._get_system_info()
        
        # Set up the main container frame
        if USE_CTK:
            self.main_frame = ctk.CTkFrame(self.root)
        else:
            self.main_frame = ttk.Frame(self.root, style="TFrame")
        
        self.main_frame.pack(fill="both", expand=True)
    
    def _get_system_info(self):
        """
        Get system information for use in the installer.
        
        Returns:
            dict: System information.
        """
        return {
            'os': determine_operating_system(),
            'admin': is_admin(),
            'py_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        }
    
    def register_page(self, page_id, page_class, *args, **kwargs):
        """
        Register a wizard page.
        
        Args:
            page_id (str): Unique identifier for the page.
            page_class (class): Page class to instantiate.
            *args, **kwargs: Arguments to pass to the page constructor.
            
        Returns:
            The instantiated page object.
        """
        if page_id in self.pages:
            logger.warning(f"Page {page_id} already registered, overwriting")
        
        # Create the page instance
        page = page_class(self.main_frame, self, *args, **kwargs)
        
        # Store the page
        self.pages[page_id] = page
        self.page_order.append(page_id)
        
        # Hide the page initially
        page.hide()
        
        return page
    
    def start(self):
        """
        Start the wizard application.
        
        Shows the first page in the page order and runs the Tkinter main loop.
        """
        if not self.pages:
            logger.error("No pages registered for the wizard")
            return
        
        # Show the first page
        self.show_page(self.page_order[0])
        
        # Start the Tkinter main loop
        self.root.mainloop()
    
    def show_page(self, page_id):
        """
        Show a specific page by ID.
        
        Args:
            page_id (str): ID of the page to show.
        """
        # Hide current page if there is one
        if self.current_page and self.current_page in self.pages:
            self.pages[self.current_page].hide()
        
        # Show the requested page
        if page_id in self.pages:
            self.pages[page_id].show()
            self.current_page = page_id
        else:
            logger.error(f"Page {page_id} not found")
    
    def next_page(self):
        """
        Navigate to the next page in the page order.
        
        Returns:
            bool: True if navigated, False if at the end.
        """
        if not self.current_page:
            return False
        
        # Find the current page index
        try:
            idx = self.page_order.index(self.current_page)
            
            # Check if there's a next page
            if idx < len(self.page_order) - 1:
                next_id = self.page_order[idx + 1]
                self.show_page(next_id)
                return True
        except ValueError:
            logger.error(f"Current page {self.current_page} not found in page order")
        
        return False
    
    def prev_page(self):
        """
        Navigate to the previous page in the page order.
        
        Returns:
            bool: True if navigated, False if at the beginning.
        """
        if not self.current_page:
            return False
        
        # Find the current page index
        try:
            idx = self.page_order.index(self.current_page)
            
            # Check if there's a previous page
            if idx > 0:
                prev_id = self.page_order[idx - 1]
                self.show_page(prev_id)
                return True
        except ValueError:
            logger.error(f"Current page {self.current_page} not found in page order")
        
        return False
    
    def set_config(self, section, data):
        """
        Store configuration data from a wizard page.
        
        Args:
            section (str): Configuration section (usually the page ID).
            data (dict): Configuration data to store.
        """
        self.config_data[section] = data
    
    def get_config(self, section=None):
        """
        Get stored configuration data.
        
        Args:
            section (str, optional): Configuration section to retrieve.
                                     If None, returns all data.
        
        Returns:
            The configuration data for the specified section or all data.
        """
        if section:
            return self.config_data.get(section, {})
        return self.config_data
    
    def run_with_progress(self, callback, progress_callback=None, done_callback=None, 
                         progress_text="Processing...", cancel_allowed=False):
        """
        Run a function in a separate thread with a progress dialog.
        
        Args:
            callback (callable): The function to run.
            progress_callback (callable, optional): Callback to update progress.
            done_callback (callable, optional): Callback when operation completes.
            progress_text (str): Text to display in the progress dialog.
            cancel_allowed (bool): Whether cancellation is allowed.
            
        Returns:
            The thread object (for reference).
        """
        # Create a progress dialog
        if USE_CTK:
            dialog = ctk.CTkToplevel(self.root)
            dialog.title("Progress")
            dialog.geometry("300x150")
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Center the dialog on the parent window
            dialog.update_idletasks()
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
            
            # Add progress components
            frame = ctk.CTkFrame(dialog)
            frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            label = ctk.CTkLabel(frame, text=progress_text)
            label.pack(pady=(0, 10))
            
            progress = ctk.CTkProgressBar(frame)
            progress.pack(fill="x", pady=10)
            
            # Start with indeterminate progress
            progress.configure(mode="indeterminate")
            progress.start()
            
            if cancel_allowed:
                cancel_button = ctk.CTkButton(frame, text="Cancel", command=lambda: setattr(thread, "cancelled", True))
                cancel_button.pack(pady=10)
        else:
            dialog = tk.Toplevel(self.root)
            dialog.title("Progress")
            dialog.geometry("300x150")
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Center the dialog on the parent window
            dialog.update_idletasks()
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
            
            # Add progress components
            frame = ttk.Frame(dialog)
            frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            label = ttk.Label(frame, text=progress_text)
            label.pack(pady=(0, 10))
            
            progress = ttk.Progressbar(frame, mode="indeterminate")
            progress.pack(fill="x", pady=10)
            progress.start()
            
            if cancel_allowed:
                cancel_button = ttk.Button(frame, text="Cancel", command=lambda: setattr(thread, "cancelled", True))
                cancel_button.pack(pady=10)
        
        # Create a worker thread
        def worker():
            result = None
            error = None
            
            try:
                result = callback()
            except Exception as e:
                error = e
                logger.exception("Error in worker thread")
            
            # Update the UI in the main thread
            dialog.after(0, lambda: on_done(result, error))
        
        def update_progress(value, text=None):
            if dialog.winfo_exists():
                if text:
                    label.configure(text=text)
                
                if value is not None and 0 <= value <= 1:
                    if USE_CTK:
                        # Switch to determinate mode if needed
                        if progress.cget("mode") == "indeterminate":
                            progress.stop()
                            progress.configure(mode="determinate")
                        progress.set(value)
                    else:
                        # Switch to determinate mode if needed
                        if progress["mode"] == "indeterminate":
                            progress.stop()
                            progress["mode"] = "determinate"
                        progress["value"] = value * 100
        
        def on_done(result, error):
            if dialog.winfo_exists():
                dialog.destroy()
            
            if done_callback:
                done_callback(result, error)
        
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.cancelled = False
        
        # Store reference to update function
        if progress_callback:
            thread.update_progress = update_progress
        
        thread.start()
        return thread
    
    def show_message(self, title, message, message_type="info"):
        """
        Show a message dialog.
        
        Args:
            title (str): Dialog title.
            message (str): Message to display.
            message_type (str): Message type ("info", "warning", "error").
        """
        if USE_CTK:
            dialog = ctk.CTkToplevel(self.root)
            dialog.title(title)
            dialog.geometry("400x200")
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Center the dialog on the parent window
            dialog.update_idletasks()
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
            
            # Add message components
            frame = ctk.CTkFrame(dialog)
            frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Icon or color based on message type
            if message_type == "warning":
                title_color = "orange"
            elif message_type == "error":
                title_color = "red"
            else:  # info
                title_color = "blue"
            
            title_label = ctk.CTkLabel(frame, text=title, font=("Arial", 16, "bold"))
            title_label.configure(text_color=title_color)
            title_label.pack(pady=(0, 10))
            
            msg_label = ctk.CTkLabel(frame, text=message, wraplength=360)
            msg_label.pack(pady=10)
            
            # OK button
            ok_button = ctk.CTkButton(frame, text="OK", command=dialog.destroy)
            ok_button.pack(pady=10)
        else:
            import tkinter.messagebox as messagebox
            
            if message_type == "warning":
                messagebox.showwarning(title, message)
            elif message_type == "error":
                messagebox.showerror(title, message)
            else:  # info
                messagebox.showinfo(title, message)
    
    def exit(self):
        """
        Close the wizard application.
        """
        self.root.destroy()


class BasePage:
    """
    Base class for wizard pages.
    
    All wizard pages should inherit from this class and override
    the setup_ui, validate, and apply methods.
    """
    
    def __init__(self, parent, wizard):
        """
        Initialize the wizard page.
        
        Args:
            parent: Parent container widget.
            wizard: Reference to the wizard application.
        """
        self.parent = parent
        self.wizard = wizard
        
        # Create the main frame for this page
        if USE_CTK:
            self.frame = ctk.CTkFrame(parent)
        else:
            self.frame = ttk.Frame(parent)
        
        # Set up the UI elements for this page
        self.setup_ui()
        
        # Add navigation buttons
        self.add_navigation_buttons()
    
    def setup_ui(self):
        """
        Set up the UI elements for this page.
        
        This method should be overridden by subclasses.
        """
        if USE_CTK:
            label = ctk.CTkLabel(self.frame, text="Base Page - Override This")
            label.pack(pady=20)
        else:
            label = ttk.Label(self.frame, text="Base Page - Override This")
            label.pack(pady=20)
    
    def add_navigation_buttons(self):
        """
        Add navigation buttons (Back, Next, Finish) to the page.
        """
        if USE_CTK:
            button_frame = ctk.CTkFrame(self.frame)
            button_frame.pack(side="bottom", fill="x", padx=20, pady=20)
            
            self.back_button = ctk.CTkButton(button_frame, text="Back", command=self.on_back)
            self.back_button.pack(side="left", padx=5)
            
            self.next_button = ctk.CTkButton(button_frame, text="Next", command=self.on_next)
            self.next_button.pack(side="right", padx=5)
            
            self.finish_button = ctk.CTkButton(button_frame, text="Finish", command=self.on_finish)
            self.finish_button.pack(side="right", padx=5)
            
            # Hide finish button by default (only shown on last page)
            self.finish_button.pack_forget()
        else:
            button_frame = ttk.Frame(self.frame)
            button_frame.pack(side="bottom", fill="x", padx=20, pady=20)
            
            self.back_button = ttk.Button(button_frame, text="Back", command=self.on_back)
            self.back_button.pack(side="left", padx=5)
            
            self.next_button = ttk.Button(button_frame, text="Next", command=self.on_next)
            self.next_button.pack(side="right", padx=5)
            
            self.finish_button = ttk.Button(button_frame, text="Finish", command=self.on_finish)
            self.finish_button.pack(side="right", padx=5)
            
            # Hide finish button by default (only shown on last page)
            self.finish_button.pack_forget()
    
    def on_back(self):
        """
        Handle the Back button click.
        """
        self.wizard.prev_page()
    
    def on_next(self):
        """
        Handle the Next button click.
        
        Validates the page data and navigates to the next page if valid.
        """
        # Validate the page data
        if self.validate():
            # Apply the page data to the wizard configuration
            self.apply()
            
            # Navigate to the next page
            self.wizard.next_page()
    
    def on_finish(self):
        """
        Handle the Finish button click.
        
        Validates the page data and completes the wizard if valid.
        """
        # Validate the page data
        if self.validate():
            # Apply the page data to the wizard configuration
            self.apply()
            
            # Complete the wizard
            self.wizard.exit()
    
    def validate(self):
        """
        Validate the page data.
        
        This method should be overridden by subclasses.
        
        Returns:
            bool: True if the data is valid, False otherwise.
        """
        return True
    
    def apply(self):
        """
        Apply the page data to the wizard configuration.
        
        This method should be overridden by subclasses.
        """
        pass
    
    def show(self):
        """
        Show this page.
        """
        self.frame.pack(fill="both", expand=True)
        
        # Adjust buttons based on page position
        wizard_pages = self.wizard.page_order
        current_idx = wizard_pages.index(self.wizard.current_page)
        
        if current_idx == 0:
            # First page - hide back button
            self.back_button.pack_forget()
        else:
            # Not first page - show back button
            self.back_button.pack(side="left", padx=5)
        
        if current_idx == len(wizard_pages) - 1:
            # Last page - show finish button, hide next button
            self.next_button.pack_forget()
            self.finish_button.pack(side="right", padx=5)
        else:
            # Not last page - show next button, hide finish button
            self.finish_button.pack_forget()
            self.next_button.pack(side="right", padx=5)
    
    def hide(self):
        """
        Hide this page.
        """
        self.frame.pack_forget() 