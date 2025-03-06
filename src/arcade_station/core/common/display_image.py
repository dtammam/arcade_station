import sys
import os
import threading
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt
import logging

# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from arcade_station.core.common.core_functions import load_toml_config, log_message

# Global variable to hold the window instance
window_instance = None
app = None

PID_FILE = "arcade_station_image.pid"  # Use a relative path or specify a directory

class ImageWindow(QMainWindow):
    def __init__(self, image_path, background_color='black', screen_geometry=None):
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
        # Method to update the image
        pixmap = QPixmap(image_path)
        self.label.setPixmap(pixmap)

    def close_window(self):
        # Method to close the window programmatically
        self.close()

def list_monitors():
    """
    List available monitors and their geometries.
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
    Display an image based on configuration from a TOML file.
    If use_default is True then the default_image_path is used.
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
    app = QApplication(sys.argv)
    window = ImageWindow(image_path, background_color)
    window.show()
    sys.exit(app.exec_())

def run_image_display(image_path, background_color, monitor_index):
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
    Function to create and display an ImageWindow in a separate process.
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
import sys
import os
import argparse
import logging

# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

from arcade_station.core.common.display_image import run_image_display

def main():
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description='Display an image on a monitor')
        parser.add_argument('image_path', help='Path to the image file to display')
        parser.add_argument('background_color', help='Background color (e.g., "black", "#000000")')
        parser.add_argument('monitor_index', type=int, help='Index of the monitor to display on')
        parser.add_argument('--identifier', default='marquee_image', help='Process identifier')
        
        args = parser.parse_args()
        
        # Verify image file exists
        if not os.path.exists(args.image_path):
            logging.error(f"Image file not found: {args.image_path}")
            sys.exit(1)
            
        logging.debug(f"Starting image display - Image: {args.image_path}, Color: {args.background_color}, Monitor: {args.monitor_index}")
        
        # Run the image display function
        run_image_display(args.image_path, args.background_color, args.monitor_index)
    
    except Exception as e:
        logging.error(f"Error in image display script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
""")
    
    # Use the standardized launch_script function with marquee_image identifier
    from arcade_station.core.common.core_functions import launch_script
    process = launch_script(
        script_path, 
        identifier="marquee_image",
        extra_args=[image_path, background_color, str(monitor_index)]
    )
    return process