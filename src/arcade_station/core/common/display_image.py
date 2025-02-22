import sys
import os
import threading
import multiprocessing
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt
import logging

# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from core.common.core_functions import load_toml_config

# Global variable to hold the window instance
window_instance = None
app = None

PID_FILE = "arcade_station_image.pid"  # Use a relative path or specify a directory

class ImageWindow(QMainWindow):
    def __init__(self, image_path, background_color='black', screen_geometry=None):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Set the background color for the entire window
        self.setStyleSheet(f"background-color: {background_color};")

        # Load the image
        pixmap = QPixmap(image_path)

        # Calculate the aspect ratio
        aspect_ratio = pixmap.height() / pixmap.width()

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

def run_app(image_path, background_color, screen_geometry, close_event):
    # If no event is provided, create one that never gets set
    if close_event is None:
        close_event = threading.Event()

    app = QApplication(sys.argv)
    window = ImageWindow(image_path, background_color, screen_geometry)
    window.show()

    def check_close_event():
        while not close_event.is_set():
            app.processEvents()
        window.close()

    close_thread = threading.Thread(target=check_close_event)
    close_thread.start()

    app.exec_()

    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

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

    app = QApplication(sys.argv)
    screens = app.screens()
    if not screens:
        print("No screens detected. Ensure you are running in a GUI-capable environment.")
        return

    if monitor_index >= len(screens):
        print(f"Monitor index {monitor_index} is out of range. Defaulting to primary monitor.")
        monitor_index = 0

    screen = screens[monitor_index]
    process = multiprocessing.Process(
        target=run_app,
        args=(image_path, background_color, screen.geometry(), close_event),
        name="arcade_station-image"
    )
    process.start()
    return process

def close_image_window():
    """
    Close the image window if it is open.
    """
    # This function will need to be adapted to communicate with the process
    # For example, using a shared variable or a signal to indicate the window should close.
    pass

def main(image_path, background_color='black'):
    app = QApplication(sys.argv)
    window = ImageWindow(image_path, background_color)
    window.show()
    sys.exit(app.exec_())

def run_image_display(image_path, background_color, monitor_index):
    app = QApplication(sys.argv)
    screens = app.screens()
    if not screens:
        logging.error("No screens detected. Ensure you are running in a GUI-capable environment.")
        return

    # Ensure the monitor index is within range
    if monitor_index >= len(screens):
        logging.warning(f"Monitor index {monitor_index} is out of range. Defaulting to primary monitor.")
        monitor_index = 0

    screen_geometry = screens[monitor_index].geometry()

    window = ImageWindow(image_path, background_color, screen_geometry)
    window.show()

    # Start the application event loop
    logging.debug("Starting application event loop for image display.")
    app.exec_()
    logging.debug("Exited application event loop for image display.")

def display_image(image_path, background_color='black'):
    """
    Function to create and display an ImageWindow in a separate process.
    """
    logging.debug(f"Displaying image: {image_path} on monitor with background color: {background_color}")

    # Load display configuration
    display_config = load_toml_config('display_config.toml')
    monitor_index = display_config['display'].get('monitor_index', 0)

    # Start the image display in a separate process
    process = multiprocessing.Process(target=run_image_display, args=(image_path, background_color, monitor_index))
    process.start()