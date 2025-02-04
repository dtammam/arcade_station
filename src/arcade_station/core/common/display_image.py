import sys
import os
import threading
import multiprocessing
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt

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

        # Set the background color or make it transparent
        if background_color.lower() == 'transparent':
            self.setAttribute(Qt.WA_TranslucentBackground, True)
        else:
            self.setStyleSheet(f"background-color: {background_color};")

        # Load the image
        pixmap = QPixmap(image_path)

        # Create a label to display the image
        self.label = QLabel(self)
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)

        # Determine the screen width and set the window size accordingly
        screen_width = screen_geometry.width() if screen_geometry else QApplication.primaryScreen().size().width()
        aspect_ratio = pixmap.height() / pixmap.width()
        window_height = int(screen_width * aspect_ratio)

        # Calculate the position to center the window
        x_position = screen_geometry.x() + (screen_geometry.width() - screen_width) // 2
        y_position = screen_geometry.y() + (screen_geometry.height() - window_height) // 2

        # Set the window geometry
        self.setGeometry(x_position, y_position, screen_width, window_height)

        # Set the label to fill the window
        self.label.setGeometry(self.rect())

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
    app = QApplication(sys.argv)
    window = ImageWindow(image_path, background_color, screen_geometry)
    window.show()

    # Check for the close event in a separate thread
    def check_close_event():
        while not close_event.is_set():
            app.processEvents()
        window.close()

    # Start the close event checker in a separate thread
    close_thread = threading.Thread(target=check_close_event)
    close_thread.start()

    app.exec_()

    # Clean up the PID file on exit
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

def display_image_from_config(config_path='display_config.toml', close_event=None):
    """
    Display an image based on configuration from a TOML file.
    """
    config = load_toml_config(config_path)
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
    process = multiprocessing.Process(target=run_app, args=(image_path, background_color, screen.geometry(), close_event), name="arcade_station-image")
    process.start()
    return process

def close_image_window():
    """
    Close the image window if it is open.
    """
    # This function will need to be adapted to communicate with the process
    # For example, using a shared variable or a signal to indicate the window should close

def main(image_path, background_color='black'):
    app = QApplication(sys.argv)
    window = ImageWindow(image_path, background_color)
    window.show()
    sys.exit(app.exec_())


def display_image(image_path, background_color='black'):
    """
    Function to create and display an ImageWindow.
    """
    app = QApplication(sys.argv)
    window = ImageWindow(image_path, background_color)
    window.show()
    sys.exit(app.exec_())