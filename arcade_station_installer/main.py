#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Arcade Station Installer - Main Entry Point
"""
import os
import sys
import tkinter as tk
from tkinter import ttk

# Add the parent directory to sys.path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import installer modules
from installer.ui.app import InstallerApp

def setup_styles():
    """Set up the ttk styles for the application."""
    style = ttk.Style()
    
    # Configure the TFrame style
    style.configure("TFrame", background="#f5f5f5")
    
    # Configure the TLabel style
    style.configure("TLabel", background="#f5f5f5", font=("Arial", 10))
    
    # Configure the TButton style
    style.configure("TButton", font=("Arial", 10))
    
    # Configure the TCheckbutton style
    style.configure("TCheckbutton", background="#f5f5f5", font=("Arial", 10))
    
    # Configure the TRadiobutton style
    style.configure("TRadiobutton", background="#f5f5f5", font=("Arial", 10))
    
    # Configure the TEntry style
    style.configure("TEntry", font=("Arial", 10))
    
    # Configure the TCombobox style
    style.configure("TCombobox", font=("Arial", 10))
    
    # Configure the title label style
    style.configure("Title.TLabel", font=("Arial", 16, "bold"))
    
    # Configure the subtitle label style
    style.configure("Subtitle.TLabel", font=("Arial", 12, "italic"))
    
    # Configure the navigation buttons
    style.configure("Navigation.TButton", font=("Arial", 10, "bold"))
    
    # Configure the header frame
    style.configure("Header.TFrame", background="#3498db")
    
    # Configure the header title
    style.configure("Header.TLabel", 
                   background="#3498db", 
                   foreground="white", 
                   font=("Arial", 14, "bold"))
    
    # Configure the header subtitle
    style.configure("HeaderSub.TLabel", 
                   background="#3498db", 
                   foreground="white", 
                   font=("Arial", 10))

def set_application_icon(root):
    """Set the application icon for the window.
    
    Args:
        root: The tkinter root window
    """
    # Get the absolute path to the icon file
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "installer", "icon.ico")
    
    if os.path.exists(icon_path):
        try:
            if sys.platform == "win32":
                root.iconbitmap(icon_path)
            else:
                # For Linux/Mac, try to use PNG if available
                png_path = icon_path.replace('.ico', '.png')
                if os.path.exists(png_path):
                    img = tk.PhotoImage(file=png_path)
                    root.tk.call('wm', 'iconphoto', root._w, img)
        except Exception:
            pass  # Silently fail if icon can't be set

def main():
    """Run the Arcade Station Installer."""
    # Create the root window
    root = tk.Tk()
    root.title("Arcade Station Installer")
    root.geometry("1000x750")  # Increased window size
    root.minsize(900, 700)     # Increased minimum size
    
    # Set application icon
    set_application_icon(root)
    
    # Set up styles
    setup_styles()
    
    # Create the application
    app = InstallerApp(root)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main() 