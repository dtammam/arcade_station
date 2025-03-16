"""
Monitor ITGMania song selection log file and update the marquee display.

This script watches a specified file for changes. When the file is updated,
it reads the file to find a banner line, extracts the image path, and 
updates the marquee display using the display_image function.
"""

import os
import sys
import time
import re
from pathlib import Path
import platform
import subprocess

# Add the parent directory of 'arcade_station' to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from arcade_station.core.common.core_functions import (
    load_toml_config, 
    log_message,
    kill_process_by_identifier
)
from arcade_station.core.common.display_image import display_image

def ensure_required_packages():
    """
    Check for and install required packages if they're missing.
    """
    if platform.system() != "Windows":
        return
    
    try:
        import win32gui
        import win32process
        import win32con
        import psutil
        log_message("All required Windows modules available", "BANNER")
    except ImportError:
        log_message("Installing required Windows packages for focus management...", "BANNER")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32", "psutil"])
            log_message("Successfully installed required packages", "BANNER")
            # Need to restart the script to use newly installed packages
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            log_message(f"Failed to install required packages: {str(e)}", "BANNER")

# Import Windows-specific modules for window focus
if platform.system() == "Windows":
    try:
        import win32gui
        import win32process
        import win32con
        import psutil
        has_win32_modules = True
    except ImportError:
        log_message("Windows modules not available for focus management", "BANNER")
        has_win32_modules = False
else:
    has_win32_modules = False

def find_itgmania_window():
    """
    Find the ITGMania window by looking for windows with 'ITGmania' in the title.
    Returns the window handle or None if not found.
    """
    if not has_win32_modules:
        return None
        
    result = None
    
    def enum_windows_callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if 'ITGmania' in window_title:
                results.append(hwnd)
        return True
        
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    
    if windows:
        return windows[0]  # Return first found ITGMania window
    return None

def refocus_itgmania():
    """
    Attempt to find the ITGMania window and ensure it has focus.
    """
    if not has_win32_modules:
        return False
        
    try:
        hwnd = find_itgmania_window()
        if hwnd:
            # First make sure the window is not minimized
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            # Set the window as foreground
            win32gui.SetForegroundWindow(hwnd)
            log_message("Refocused ITGMania window", "BANNER")
            return True
        else:
            log_message("ITGMania window not found for refocusing", "BANNER")
            return False
    except Exception as e:
        log_message(f"Failed to refocus ITGMania window: {str(e)}", "BANNER")
        return False

def monitor_itgmania_log(config_path='display_config.toml'):
    """
    Monitor the ITGMania log file for changes and update the marquee display.
    
    Args:
        config_path (str): Path to the display configuration file.
    """
    # Load configuration
    try:
        config = load_toml_config(config_path)
        dynamic_marquee_config = config.get('dynamic_marquee', {})
        display_config = config.get('display', {})
        
        # Check if ITGMania display is enabled
        if not dynamic_marquee_config.get('itgmania_display_enabled', False):
            log_message("ITGMania display is disabled in configuration", "BANNER")
            return
        
        # Get the log file path
        log_file_path = dynamic_marquee_config.get('itgmania_display_file_path')
        
        if not log_file_path:
            log_message("ITGMania log file path not specified in configuration", "BANNER")
            return
        
        # Verify log file directory exists and resolve any user variables in path
        log_file_path = os.path.expanduser(log_file_path)
        log_file_path = os.path.normpath(log_file_path)
        log_file = Path(log_file_path)
        
        log_message(f"Using resolved ITGMania log file path: {log_file}", "BANNER")
        
        if not log_file.parent.exists():
            log_message(f"Directory for ITGMania log file does not exist: {log_file.parent}", "BANNER")
            log_message(f"Will attempt to create directory: {log_file.parent}", "BANNER")
            try:
                log_file.parent.mkdir(parents=True, exist_ok=True)
                log_message(f"Created directory: {log_file.parent}", "BANNER")
            except Exception as e:
                log_message(f"Failed to create directory: {str(e)}", "BANNER")
                return
        
        # Create the file if it doesn't exist
        if not log_file.exists():
            log_file.touch()
            log_message(f"Created ITGMania log file: {log_file}", "BANNER")
        
        # Get initial modification time
        last_mod_time = log_file.stat().st_mtime
        
        log_message(f"Monitoring ITGMania log file: {log_file}", "BANNER")
        
        # Main monitoring loop
        while True:
            try:
                # Check if the file exists
                if log_file.exists():
                    # Get current modification time
                    current_mod_time = log_file.stat().st_mtime
                    
                    # If the file has been modified
                    if current_mod_time > last_mod_time:
                        log_message(f"ITGMania log file updated: {log_file}", "BANNER")
                        update_marquee_from_file(str(log_file), config)
                        
                        # Small delay to ensure the file is not being written to
                        time.sleep(1)
                        
                        # Update last modification time
                        last_mod_time = current_mod_time
                else:
                    log_message(f"ITGMania log file no longer exists: {log_file}", "BANNER")
                    log_message("Attempting to recreate the file", "BANNER")
                    try:
                        log_file.touch()
                        log_message(f"Recreated ITGMania log file: {log_file}", "BANNER")
                        last_mod_time = log_file.stat().st_mtime
                    except Exception as e:
                        log_message(f"Failed to recreate log file: {str(e)}", "BANNER")
            except Exception as e:
                log_message(f"Error monitoring ITGMania log file: {str(e)}", "BANNER")
            
            # Sleep to prevent high CPU usage
            time.sleep(1)
            
    except Exception as e:
        log_message(f"Failed to monitor ITGMania log file: {str(e)}", "BANNER")


def update_marquee_from_file(file_path, config):
    """
    Parse the ITGMania log file and update the marquee with the banner image.
    
    Args:
        file_path (str): Path to the ITGMania log file.
        config (dict): Display configuration.
    """
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Kill any existing marquee image process before displaying a new one
        log_message("Killing any existing marquee image processes", "BANNER")
        kill_process_by_identifier("marquee_image")
        
        # Get essential properties from config
        background_color = config.get('display', {}).get('background_color', 'black')
        itgmania_base_path = config.get('dynamic_marquee', {}).get('itgmania_base_path', '')
        
        # Check for event type and extract banner path
        event_match = re.search(r'Event: (\w+)', content, re.MULTILINE)
        banner_match = re.search(r'Banner: (.+)$', content, re.MULTILINE)
        
        # Handle the event based on its type
        if event_match:
            event_type = event_match.group(1).strip()
            log_message(f"Found event: {event_type}", "BANNER")
            
            # Handle different event types
            if event_type == "Chosen" and banner_match:
                # Handle song selection - get and process the banner path
                banner_path = banner_match.group(1).strip()
                log_message(f"Found banner path: {banner_path}", "BANNER")
                
                # Process relative paths if needed
                if (banner_path.startswith('/') or banner_path.startswith('\\')) and not banner_path[1:2] == ':':
                    banner_path = banner_path.lstrip('/\\')
                    if itgmania_base_path:
                        full_banner_path = os.path.join(itgmania_base_path, banner_path)
                        banner_path = full_banner_path
                        log_message(f"Resolved relative path: {banner_path}", "BANNER")
                
                # Normalize backslashes to forward slashes
                banner_path = banner_path.replace('\\', '/')
                
                # Display the banner if it exists
                if os.path.exists(banner_path):
                    display_image(banner_path, background_color)
                    log_message(f"Showing song banner: {banner_path}", "BANNER")
            elif banner_match:
                # For other events with a banner path, use that
                banner_path = banner_match.group(1).strip()
                log_message(f"Found banner path for event {event_type}: {banner_path}", "BANNER")
                
                # Process relative paths if needed
                if (banner_path.startswith('/') or banner_path.startswith('\\')) and not banner_path[1:2] == ':':
                    banner_path = banner_path.lstrip('/\\')
                    if itgmania_base_path:
                        full_banner_path = os.path.join(itgmania_base_path, banner_path)
                        banner_path = full_banner_path
                        log_message(f"Resolved relative path: {banner_path}", "BANNER")
                
                # Normalize backslashes to forward slashes
                banner_path = banner_path.replace('\\', '/')
                
                # Display the banner if it exists
                if os.path.exists(banner_path):
                    display_image(banner_path, background_color)
                    log_message(f"Showing banner for {event_type}: {banner_path}", "BANNER")
        
        # Wait a moment for the display to update
        time.sleep(0.5)
        
        # Ensure ITGMania window has focus
        refocus_itgmania()
    except Exception as e:
        log_message(f"Error updating marquee from file: {str(e)}", "BANNER")


if __name__ == "__main__":
    # Ensure we have required packages
    ensure_required_packages()
    
    # Start monitoring
    monitor_itgmania_log() 