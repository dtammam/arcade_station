"""
Welcome Page for Arcade Station Installer.

This module provides the welcome page for the Arcade Station installer,
introducing users to the installation process.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path

# Import from parent directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from wizard.base_wizard import BasePage

# Import CustomTkinter if available
try:
    import customtkinter as ctk
    USE_CTK = True
except ImportError:
    USE_CTK = False

class WelcomePage(BasePage):
    """
    Welcome page for the Arcade Station installer.
    
    This page introduces users to Arcade Station and the installation process.
    """
    
    def setup_ui(self):
        """
        Set up the UI elements for the welcome page.
        """
        # Use CustomTkinter or standard Tkinter based on availability
        if USE_CTK:
            # Main container
            content_frame = ctk.CTkFrame(self.frame)
            content_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Header
            header_frame = ctk.CTkFrame(content_frame)
            header_frame.pack(fill="x", pady=(0, 20))
            
            # Logo image if available
            logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'assets', 'images', 'arcade_station_logo.png'))
            if os.path.exists(logo_path):
                try:
                    logo_img = ctk.CTkImage(light_image=tk.PhotoImage(file=logo_path), size=(200, 100))
                    logo_label = ctk.CTkLabel(header_frame, image=logo_img, text="")
                    logo_label.pack(pady=10)
                except Exception:
                    # Fallback to text if image loading fails
                    title_label = ctk.CTkLabel(header_frame, text="Arcade Station", font=("Arial", 24, "bold"))
                    title_label.pack(pady=10)
            else:
                # Fallback to text if image not available
                title_label = ctk.CTkLabel(header_frame, text="Arcade Station", font=("Arial", 24, "bold"))
                title_label.pack(pady=10)
            
            # Welcome message
            welcome_msg = (
                "Welcome to the Arcade Station Installer!\n\n"
                "This wizard will guide you through the process of setting up "
                "Arcade Station on your system. You'll be able to customize "
                "various aspects of your installation including:\n\n"
                "• Installation location\n"
                "• Display configuration\n"
                "• Game setup\n"
                "• Control bindings\n"
                "• Utility features\n\n"
                "Click 'Next' to begin the installation process."
            )
            
            text_area = ctk.CTkTextbox(content_frame, height=250, width=500)
            text_area.pack(fill="both", expand=True, padx=10, pady=10)
            text_area.insert("1.0", welcome_msg)
            text_area.configure(state="disabled")
            
            # System information
            info_frame = ctk.CTkFrame(content_frame)
            info_frame.pack(fill="x", pady=10)
            
            info_label = ctk.CTkLabel(info_frame, text="System Information:", font=("Arial", 12, "bold"))
            info_label.pack(anchor="w", padx=10, pady=(10, 5))
            
            # Get system info from wizard
            sys_info = self.wizard.system_info
            os_info = f"Operating System: {sys_info.get('os', 'Unknown')}"
            admin_info = f"Admin Privileges: {'Yes' if sys_info.get('admin', False) else 'No'}"
            py_info = f"Python Version: {sys_info.get('py_version', 'Unknown')}"
            
            os_label = ctk.CTkLabel(info_frame, text=os_info)
            os_label.pack(anchor="w", padx=20, pady=2)
            
            admin_label = ctk.CTkLabel(info_frame, text=admin_info)
            admin_label.pack(anchor="w", padx=20, pady=2)
            
            py_label = ctk.CTkLabel(info_frame, text=py_info)
            py_label.pack(anchor="w", padx=20, pady=2)
            
            # Admin warning if needed
            if sys_info.get('os') == 'Windows' and not sys_info.get('admin', False):
                warning_label = ctk.CTkLabel(
                    info_frame, 
                    text="Warning: Administrator privileges are required for some features.",
                    text_color="orange"
                )
                warning_label.pack(anchor="w", padx=20, pady=(5, 10))
        else:
            # Fallback to standard Tkinter
            # Main container
            content_frame = ttk.Frame(self.frame)
            content_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Header
            header_frame = ttk.Frame(content_frame)
            header_frame.pack(fill="x", pady=(0, 20))
            
            # Logo image if available
            logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'assets', 'images', 'arcade_station_logo.png'))
            if os.path.exists(logo_path):
                try:
                    logo_img = tk.PhotoImage(file=logo_path)
                    logo_img = logo_img.subsample(2, 2)  # Reduce size
                    logo_label = ttk.Label(header_frame, image=logo_img)
                    logo_label.image = logo_img  # Keep reference
                    logo_label.pack(pady=10)
                except Exception:
                    # Fallback to text if image loading fails
                    title_label = ttk.Label(header_frame, text="Arcade Station", font=("Arial", 24, "bold"))
                    title_label.pack(pady=10)
            else:
                # Fallback to text if image not available
                title_label = ttk.Label(header_frame, text="Arcade Station", font=("Arial", 24, "bold"))
                title_label.pack(pady=10)
            
            # Welcome message
            welcome_msg = (
                "Welcome to the Arcade Station Installer!\n\n"
                "This wizard will guide you through the process of setting up "
                "Arcade Station on your system. You'll be able to customize "
                "various aspects of your installation including:\n\n"
                "• Installation location\n"
                "• Display configuration\n"
                "• Game setup\n"
                "• Control bindings\n"
                "• Utility features\n\n"
                "Click 'Next' to begin the installation process."
            )
            
            text_area = tk.Text(content_frame, height=15, width=60)
            text_area.pack(fill="both", expand=True, padx=10, pady=10)
            text_area.insert("1.0", welcome_msg)
            text_area.configure(state="disabled")
            
            # System information
            info_frame = ttk.Frame(content_frame)
            info_frame.pack(fill="x", pady=10)
            
            info_label = ttk.Label(info_frame, text="System Information:", font=("Arial", 12, "bold"))
            info_label.pack(anchor="w", padx=10, pady=(10, 5))
            
            # Get system info from wizard
            sys_info = self.wizard.system_info
            os_info = f"Operating System: {sys_info.get('os', 'Unknown')}"
            admin_info = f"Admin Privileges: {'Yes' if sys_info.get('admin', False) else 'No'}"
            py_info = f"Python Version: {sys_info.get('py_version', 'Unknown')}"
            
            os_label = ttk.Label(info_frame, text=os_info)
            os_label.pack(anchor="w", padx=20, pady=2)
            
            admin_label = ttk.Label(info_frame, text=admin_info)
            admin_label.pack(anchor="w", padx=20, pady=2)
            
            py_label = ttk.Label(info_frame, text=py_info)
            py_label.pack(anchor="w", padx=20, pady=2)
            
            # Admin warning if needed
            if sys_info.get('os') == 'Windows' and not sys_info.get('admin', False):
                warning_label = ttk.Label(
                    info_frame, 
                    text="Warning: Administrator privileges are required for some features.",
                    foreground="orange"
                )
                warning_label.pack(anchor="w", padx=20, pady=(5, 10))
    
    def validate(self):
        """
        Validate the page data.
        
        The welcome page has no data to validate, so always returns True.
        
        Returns:
            bool: Always True.
        """
        return True
    
    def apply(self):
        """
        Apply the page data to the wizard configuration.
        
        The welcome page has no data to apply.
        """
        pass 