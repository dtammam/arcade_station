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
    
    # Available themes: ('clam', 'alt', 'default', 'classic')
    # Use 'clam' for a more modern look
    style.theme_use("clam")
    
    # Configure colors for a dark theme
    bg_color = "#2d2d2d"
    fg_color = "#e0e0e0"
    accent_color = "#3498db"
    button_bg = "#444444"
    button_fg = "#ffffff"
    entry_bg = "#3d3d3d"
    entry_fg = "#ffffff"
    
    # Configure the TFrame style
    style.configure("TFrame", background=bg_color)
    
    # Configure the TLabel style
    style.configure("TLabel", background=bg_color, foreground=fg_color, font=("Arial", 10))
    
    # Configure the TButton style
    style.configure("TButton", background=button_bg, foreground=button_fg, font=("Arial", 10))
    
    # Configure the TCheckbutton style
    style.configure("TCheckbutton", background=bg_color, foreground=fg_color, font=("Arial", 10))
    
    # Configure the TRadiobutton style
    style.configure("TRadiobutton", background=bg_color, foreground=fg_color, font=("Arial", 10))
    
    # Configure the TEntry style
    style.configure("TEntry", fieldbackground=entry_bg, foreground=entry_fg, font=("Arial", 10))
    
    # Configure the TCombobox style
    style.configure("TCombobox", fieldbackground=entry_bg, foreground=entry_fg, font=("Arial", 10))
    style.map('TCombobox', fieldbackground=[('readonly', entry_bg)])
    style.map('TCombobox', selectbackground=[('readonly', button_bg)])
    style.map('TCombobox', selectforeground=[('readonly', button_fg)])
    
    # Configure the title label style
    style.configure("Title.TLabel", background=bg_color, foreground=fg_color, font=("Arial", 16, "bold"))
    
    # Configure the subtitle label style
    style.configure("Subtitle.TLabel", background=bg_color, foreground=fg_color, font=("Arial", 12, "italic"))
    
    # Configure the navigation buttons
    style.configure("Navigation.TButton", background=accent_color, foreground=button_fg, font=("Arial", 10, "bold"))
    
    # Configure the header frame
    style.configure("Header.TFrame", background=accent_color)
    
    # Configure the header title
    style.configure("Header.TLabel", 
                   background=accent_color, 
                   foreground="white", 
                   font=("Arial", 14, "bold"))
    
    # Configure the header subtitle
    style.configure("HeaderSub.TLabel", 
                   background=accent_color, 
                   foreground="white", 
                   font=("Arial", 10))
    
    # Configure canvas with dark background
    style.configure("Canvas", background=bg_color)

def main():
    """Run the Arcade Station Installer."""
    # Create the root window
    root = tk.Tk()
    root.title("Arcade Station Installer")
    root.geometry("900x700")
    root.minsize(900, 700)
    
    # Set application icon
    if sys.platform == "win32":
        # Windows icon
        try:
            root.iconbitmap("installer/resources/icon.ico")
        except tk.TclError:
            pass
    else:
        # Linux/Mac icon
        try:
            img = tk.PhotoImage(file="installer/resources/icon.png")
            root.tk.call('wm', 'iconphoto', root._w, img)
        except tk.TclError:
            pass
    
    # Set up styles
    setup_styles()
    
    # Create the application
    app = InstallerApp(root)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main() 