"""
Display Image Module for Arcade Station.

This module provides functionality to display images on specific monitors in a
non-intrusive way. It creates frameless, always-on-top windows that display images
without stealing focus from other applications, making it ideal for displaying
marquee images, banners, or overlays while games are running.

The module uses PyQt5 to create and manage the image windows, with support for
multiple monitors, background colors, and image updates.
"""

import sys
import os
import threading
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt
import logging

# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from arcade_station.core.common.core_functions import load_toml_config, log_message, launch_script

# Global variable to hold the window instance
window_instance = None
app = None

PID_FILE = "arcade_station_image.pid"  # Use a relative path or specify a directory

class ImageWindow(QMainWindow):
    """
    A frameless window that displays an image without stealing focus.
    
    This class creates a non-interactive window that stays on top of other windows
    and displays an image. It's designed to show marquee images, game art, or
    other visual elements while games are running, without interfering with the
    game's input handling.
    
    Attributes:
        image_label (QLabel): The label that contains the displayed image.
    """
    
    def __init__(self, image_path, background_color='black', screen_geometry=None):
        """
        Initialize the image window with specified parameters.
        
        Args:
            image_path (str): Path to the image file to display.
            background_color (str): Color name or hex code for the window background.
                                   Use 'transparent' for a transparent background.
            screen_geometry: The geometry of the target screen to display on.
                           If None, the primary monitor is used.
        """
        super().__init__()
        # Add Qt.Tool and Qt.NoFocus flags to prevent stealing focus
        # Qt.Tool tells Windows this is a tool window (not a main app window), they don't show in taskbar and don't steal focus
        # Qt.WindowDoesNotAcceptFocus prevents the window from accepting keyboard focus
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool | 
            Qt.WindowDoesNotAcceptFocus
        )
        
        # Add additional attribute to never activate the window
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        # Handle transparency specially
        if background_color.lower() == 'transparent':
            # Enable window transparency
            self.setAttribute(Qt.WA_TranslucentBackground)
            # Use transparent stylesheet
            self.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        else:
            # Set the background color for the entire window
            self.setStyleSheet(f"background-color: {background_color};")

        # Load the image
        pixmap = QPixmap(image_path)

        # Calculate the aspect ratio
        aspect_ratio = pixmap.height() / pixmap.width()
        
        # For transparent PNGs, ensure alpha channel is preserved
        if background_color.lower() == 'transparent' and image_path.lower().endswith('.png'):
            pixmap.setMask(pixmap.createMaskFromColor(Qt.transparent))

        # Determine the maximum size for the image to fit within the screen
        screen_width = screen_geometry.width() if screen_geometry else QApplication.primaryScreen().size().width()
        screen_height = screen_geometry.height() if screen_geometry else QApplication.primaryScreen().size().height()

        # Calculate the maximum width and height while maintaining aspect ratio
        max_width = screen_width
        max_height = int(max_width * aspect_ratio)

        if max_height > screen_height:
            max_height = screen_height
            max_width = int(max_height / aspect_ratio)

        # Set the window size to the screen size to cover the entire screen
        self.setFixedSize(screen_width, screen_height)

        # Create a label to display the image
        self.label = QLabel(self)
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)

        # Calculate the position to center the image within the window
        x_position = (screen_width - max_width) // 2
        y_position = (screen_height - max_height) // 2

        # Set the label geometry to center the image
        self.label.setGeometry(x_position, y_position, max_width, max_height)

        # Set the window geometry to cover the entire screen
        self.setGeometry(screen_geometry.x(), screen_geometry.y(), screen_width, screen_height)

    def update_image(self, image_path):
        """
        Update the displayed image without recreating the window.
        
        Args:
            image_path (str): Path to the new image file to display.
        """
        pixmap = QPixmap(image_path)
        self.label.setPixmap(pixmap)

    def close_window(self):
        """
        Close the window programmatically.
        
        This method can be called to close the window from outside the event loop.
        """
        self.close()

def list_monitors():
    """
    Retrieve information about all connected monitors.
    
    Gets details about each connected display, including its index number,
    name, and geometry (position and dimensions).
    
    Returns:
        list: A list of dictionaries, each containing information about a monitor:
              - index: The monitor index (0-based)
              - name: The display name
              - geometry: A tuple (x, y, width, height) representing the monitor's position and size
    """
    app = QApplication(sys.argv)
    screens = app.screens()
    monitor_info = []
    for index, screen in enumerate(screens):
        geometry = screen.geometry()
        monitor_info.append({
            'index': index,
            'name': screen.name(),
            'geometry': (geometry.x(), geometry.y(), geometry.width(), geometry.height())
        })
    return monitor_info

def display_image_from_config(config_path='display_config.toml', close_event=None, use_default=False):
    """
    Display an image using parameters specified in a configuration file.
    
    Reads display settings from a TOML configuration file, including image path,
    target monitor, and background color. Can optionally use a default image
    instead of the configured one.
    
    Args:
        config_path (str): Path to the TOML configuration file.
        close_event (threading.Event, optional): Event that will signal when to close the window.
        use_default (bool): If True, uses the default_image_path from config instead of image_path.
    
    Returns:
        None
    """
    config = load_toml_config(config_path)
    if use_default:
        image_path = config['display'].get('default_image_path', config['display']['image_path'])
    else:
        image_path = config['display']['image_path']
    background_color = config['display']['background_color']
    monitor_index = config['display'].get('monitor_index', 0)

    log_message(f"Display image from config: {'default image' if use_default else 'normal image'}", "BANNER")
    log_message(f"Image path: {image_path}, Background color: {background_color}", "BANNER")

    # Use the display_image function which now uses the standardized approach with marquee_image identifier
    return display_image(image_path, background_color)

def main(image_path, background_color='black'):
    """
    Entry point for standalone image display functionality.
    
    Creates a QApplication and ImageWindow to display an image with the
    specified background color. This function is used when the module
    is run directly as a script.
    
    Args:
        image_path (str): Path to the image file to display.
        background_color (str): Color name or hex code for the window background.
    
    Note:
        This function calls sys.exit() and does not return.
    """
    app = QApplication(sys.argv)
    window = ImageWindow(image_path, background_color)
    window.show()
    sys.exit(app.exec_())

def run_image_display(image_path, background_color, monitor_index):
    """
    Display an image on a specific monitor with the given background color.
    
    Creates a QApplication and ImageWindow to display an image on the specified
    monitor. Handles monitor selection and ensures the window is displayed
    without stealing focus.
    
    Args:
        image_path (str): Path to the image file to display.
        background_color (str): Color name or hex code for the window background.
        monitor_index (int): Index of the monitor to display the image on.
    
    Returns:
        None
    """
    app = QApplication(sys.argv)
    screens = app.screens()
    if not screens:
        log_message("No screens detected. Ensure you are running in a GUI-capable environment.", "BANNER")
        return

    # Ensure the monitor index is within range
    if monitor_index >= len(screens):
        log_message(f"Monitor index {monitor_index} is out of range. Defaulting to primary monitor.", "BANNER")
        monitor_index = 0

    screen_geometry = screens[monitor_index].geometry()

    window = ImageWindow(image_path, background_color, screen_geometry)
    
    # Use show() instead of activating the window
    # This ensures the window is displayed without stealing focus
    window.show()
    log_message("Showing image window without stealing focus", "BANNER")

    # Disable window activation through the event queue
    app.setQuitOnLastWindowClosed(True)

    # Start the application event loop
    log_message("Starting application event loop for image display.", "BANNER")
    app.exec_()
    log_message("Exited application event loop for image display.", "BANNER")

def display_image(image_path, background_color='black'):
    """
    Display an image in a separate process to avoid blocking the main application.
    
    Launches a separate Python process to display the image, allowing the
    calling process to continue execution. Uses a dedicated script to handle
    the image display.
    
    Args:
        image_path (str): Path to the image file to display.
        background_color (str): Color name or hex code for the window background.
                               Defaults to 'black'.
    
    Returns:
        subprocess.Popen: The process object for the launched image display script.
    """
    log_message(f"Displaying image: {image_path} on monitor with background color: {background_color}", "BANNER")

    # Load display configuration
    display_config = load_toml_config('display_config.toml')
    monitor_index = display_config['display'].get('monitor_index', 0)

    # Get the path to the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(current_dir, "display_image_script.py")
    
    # Ensure the script exists and has the correct content
    if not os.path.exists(script_path):
        with open(script_path, 'w') as f:
            f.write("""
# This script is auto-generated to display images
import sys
import os
import argparse

# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

from arcade_station.core.common.display_image import display_image

def main():
    parser = argparse.ArgumentParser(description='Display an image on a specific monitor')
    parser.add_argument('image_path', help='Path to the image file')
    parser.add_argument('--background', default='black', help='Background color (default: black)')
    args = parser.parse_args()
    
    display_image(args.image_path, args.background)

if __name__ == "__main__":
    main()
""")
    
    # Use the standardized launch_script function with marquee_image identifier
    process = launch_script(
        script_path, 
        identifier="marquee_image",
        extra_args=[image_path, background_color, str(monitor_index)]
    )
    return process