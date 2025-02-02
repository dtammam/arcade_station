import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt

class ImageWindow(QMainWindow):
    def __init__(self, image_path, background_color='black'):
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

        # Set the window size to the image size
        screen_width = QApplication.primaryScreen().size().width()
        aspect_ratio = pixmap.height() / pixmap.width()
        self.setGeometry(0, 0, screen_width, int(screen_width * aspect_ratio))

        # Set the label to fill the window
        self.label.setGeometry(self.rect())

    def update_image(self, image_path):
        # Method to update the image
        pixmap = QPixmap(image_path)
        self.label.setPixmap(pixmap)

    def close_window(self):
        # Method to close the window programmatically
        self.close()

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