"""
Monitor Screenshot Module for Arcade Station.

This module provides functionality for capturing screenshots from specific monitors
in the Arcade Station system. It supports:
- Configurable monitor selection
- Adjustable image quality settings
- Optional sound effects on capture
- Cross-platform compatibility (Windows, macOS, Linux)
"""

import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QScreen
import tomllib
import subprocess

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from arcade_station.core.common.core_functions import log_message

def load_config(config_path='config/screenshot_config.toml'):
    """
    Load screenshot configuration from a TOML file.
    
    Args:
        config_path (str): Path to the configuration file. Defaults to
                          'config/screenshot_config.toml'.
    
    Returns:
        dict: Configuration dictionary containing screenshot settings.
    """
    with open(config_path, 'rb') as f:
        return tomllib.load(f)

def take_screenshot_from_config():
    """
    Take a screenshot using settings from the configuration file.
    
    Reads the screenshot configuration and calls take_screenshot() with
    the configured parameters. This is the main entry point for taking
    screenshots with default settings.
    
    Returns:
        None. The screenshot is saved to the configured location.
    """
    config = load_config()
    monitor_index = config['screenshot']['monitor_index']
    file_location = config['screenshot']['file_location']
    file_name = config['screenshot']['file_name'] or datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    quality = config['screenshot']['quality']
    take_screenshot(monitor_index, file_location, file_name, quality, config)

def take_screenshot(monitor_index=0, file_location='.', file_name=None, quality='High', config=None):
    """
    Take a screenshot of a specific monitor and save it to a file.
    
    This function captures a screenshot from the specified monitor using PyQt5,
    saves it as a JPEG file with the specified quality, and optionally plays
    a sound effect upon completion.
    
    Args:
        monitor_index (int): Index of the monitor to capture (0-based).
                            Defaults to 0 (primary monitor).
        file_location (str): Directory where the screenshot will be saved.
                            Defaults to current directory.
        file_name (str): Name of the screenshot file (without extension).
                        If None, uses current timestamp.
        quality (str): Image quality setting ('High', 'Medium', 'Low').
                      Affects JPEG compression level.
        config (dict): Configuration dictionary containing sound file settings.
                      If None, no sound will be played.
    
    Returns:
        None. The screenshot is saved to disk and a sound may be played.
    """
    app = QApplication(sys.argv)
    screens = app.screens()
    if not screens:
        log_message("No screens detected. Ensure you are running in a GUI-capable environment.", "SCREENSHOT")
        return

    if monitor_index >= len(screens):
        log_message(f"Monitor index {monitor_index} is out of range. Defaulting to primary monitor.", "SCREENSHOT")
        monitor_index = 0

    screen = screens[monitor_index]
    screenshot = screen.grabWindow(0)

    # Set default file name if not provided
    if not file_name:
        file_name = datetime.now().strftime('%Y-%m-%d %H-%M-%S')

    # Determine file path
    file_path = os.path.join(file_location, f"{file_name}.png")

    # Save the screenshot with adjustable quality
    if quality == 'High':
        screenshot.save(file_path.replace('.png', '.jpg'), 'JPEG', quality=95)
    elif quality == 'Medium':
        screenshot.save(file_path.replace('.png', '.jpg'), 'JPEG', quality=75)
    elif quality == 'Low':
        screenshot.save(file_path.replace('.png', '.jpg'), 'JPEG', quality=50)

    log_message(f"Screenshot saved to {file_path}", "SCREENSHOT")

    # Resolve the sound file path to an absolute path
    sound_file = os.path.abspath(os.path.join(os.path.dirname(__file__), config['screenshot'].get('sound_file', '')))

    # Debug: Print the resolved sound file path
    log_message(f"Resolved sound file path: {sound_file}", "SCREENSHOT")

    # Play sound if specified and exists
    if sound_file and os.path.exists(sound_file) and config['screenshot'].get('sound_file', '').strip():
        try:
            if sys.platform.startswith('win'):
                # Use hidden PowerShell window to play sound
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0  # 0 means SW_HIDE
                subprocess.run(
                    ['powershell', '-WindowStyle', 'Hidden', '-c', f'(New-Object Media.SoundPlayer "{sound_file}").PlaySync();'],
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            elif sys.platform.startswith('darwin'):
                subprocess.run(['afplay', sound_file])
            elif sys.platform.startswith('linux'):
                subprocess.run(['mpg123', sound_file])
        except Exception as e:
            log_message(f"Error playing sound: {e}", "SCREENSHOT")
    else:
        log_message("No sound file specified or file not found.", "SCREENSHOT")

    app.quit()

if __name__ == "__main__":
    take_screenshot_from_config() 