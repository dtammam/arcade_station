import sys
import os
# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from arcade_station.core.common.core_functions import *
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt

# Global variable to hold the window instance
window_instance = None

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

def display_image_from_config(config_path='display_config.toml'):
    """
    Display an image based on configuration from a TOML file.
    """
    global window_instance  # Declare the global variable
    config = load_toml_config(config_path)
    image_path = config['display']['image_path']
    background_color = config['display']['background_color']
    monitor_index = config['display'].get('monitor_index', 0)

    app = QApplication(sys.argv)
    screens = app.screens()
    if monitor_index >= len(screens):
        print(f"Monitor index {monitor_index} is out of range. Defaulting to primary monitor.")
        monitor_index = 0

    screen = screens[monitor_index]
    window_instance = ImageWindow(image_path, background_color, screen.geometry())
    window_instance.show()

    sys.exit(app.exec_())

def close_image_window():
    """
    Close the image window if it is open.
    """
    global window_instance
    if window_instance is not None:
        window_instance.close()
        window_instance = None

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