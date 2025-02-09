import sys
import os
import signal
import psutil  # Use psutil for better process management on Windows
# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from arcade_station.core.common.core_functions import *
# Image launch
from core.common.display_image import *
from PyQt5.QtWidgets import QApplication

kill_processes_from_toml('processes_to_kill.toml')
kill_process_by_identifier("open_image")
process = launch_script(
    r'C:/Repositories/arcade_station/src/arcade_station/open_image.py',
    identifier="open_image"  # This will appear in the process command-line.
)
start_pegasus()