import sys
import os
import threading
import multiprocessing
import subprocess
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt
import os
import subprocess

# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from arcade_station.core.common.core_functions import *

process = launch_script(
    r'C:/Repositories/arcade_station/src/arcade_station/open_image.py',
    identifier="open_image"  # This will appear in the process command-line.
)