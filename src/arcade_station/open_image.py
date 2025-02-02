import sys
import os
# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from arcade_station.core.common.display_image import ImageWindow
from PyQt5.QtWidgets import QApplication

def display_and_close_image(image_path, background_color='black'):
    """
    Function to create, display, and close an ImageWindow.
    """
    app = QApplication(sys.argv)
    window = ImageWindow(image_path, background_color)
    window.show()

    # Simulate some condition to close the window
    input("Press Enter to close the image...")  # Wait for user input to close
    window.close()

    sys.exit(app.exec_())

if __name__ == "__main__":
    # Example usage
    display_and_close_image("//CLEARBOOK/Games/ITGmania/Songs/In The Groove Redux/Birdie (Jasmine)/Birdie-bn.png", "transparent")