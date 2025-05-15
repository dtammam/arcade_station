#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Arcade Station Installer - Main Entry Point
"""
import os
import sys
import tkinter as tk
from tkinter import ttk
import logging
from datetime import datetime
import time

# Add the parent directory to sys.path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import installer modules
from installer.ui.app import InstallerApp

def setup_logging():
    """Set up logging configuration to consistently log to file."""
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Check for recent PowerShell log files (within the last 5 minutes)
    existing_log = None
    try:
        log_files = sorted([
            os.path.join(log_dir, f) for f in os.listdir(log_dir)
            if f.startswith("arcade_station_installer_") and f.endswith(".log")
        ], key=os.path.getmtime, reverse=True)
        
        if log_files:
            newest_log = log_files[0]
            # Check if the log file was created in the last 5 minutes
            if time.time() - os.path.getmtime(newest_log) < 300:  # 5 minutes in seconds
                existing_log = newest_log
    except Exception:
        # If there's any error finding existing logs, just continue with a new one
        pass
    
    # Create a timestamp-based log filename if there's no recent log
    if existing_log:
        log_file = existing_log
        logging.info(f"Continuing with existing log file: {log_file}")
    else:
        log_file = os.path.join(log_dir, f"arcade_station_installer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # Check if stdout is being redirected
    is_redirected = not os.isatty(sys.stdout.fileno()) if hasattr(sys.stdout, 'fileno') and callable(sys.stdout.fileno) else True
    
    # Configure logging to write to file and possibly console
    handlers = [logging.FileHandler(log_file)]
    
    # Only add console handler if not redirected or -console flag is specified
    if not is_redirected or "-console" in sys.argv:
        handlers.append(logging.StreamHandler())
    
    # Configure the logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    # Log the start of the installer
    logging.info("=== Arcade Station Installer UI Started ===")
    logging.info(f"Log file: {log_file}")
    
    return log_file

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

def hide_console_window():
    """Hide the console window on Windows."""
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.user32.ShowWindow(
                ctypes.windll.kernel32.GetConsoleWindow(), 0)
            return True
        except Exception as e:
            print(f"Failed to hide console window: {e}")
            return False
    return False

def main():
    """Run the Arcade Station Installer."""
    # Configure logging first
    log_file = setup_logging()
    
    # Don't try to hide console here since the batch file handles that
    logging.info("Installer launched from batch file")
    
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
    
    # Log end of application
    logging.info("=== Arcade Station Installer Finished ===")

if __name__ == "__main__":
    main() 