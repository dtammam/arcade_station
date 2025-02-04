import time
import sys
import os
# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Image launch
from core.common.display_image import *
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    display_image_from_config()