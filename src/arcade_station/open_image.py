import sys
import os
# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Image launch
from arcade_station.core.common.display_image import *
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    # Example usage
    display_image("C:/Repositories/arcade_station/assets/images/banners/2014.png", "transparent")
    
