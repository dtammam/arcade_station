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

# Determine the current directory of this script.
base_dir = os.path.dirname(os.path.abspath(__file__))

# Construct absolute paths to the relative scripts.
listener_script = os.path.join(base_dir, "listeners", "key_listener.py")
pegasus_script = os.path.join(base_dir, "start_pegasus.py")


# Launch the key_listener.py script with the appropriate identifier.
listener_process = launch_script(listener_script, identifier="key_listener")
print(f"Launched key_listener.py with PID: {listener_process.pid}")



# Launch the start_pegasus.py script with its identifier.
pegasus_process = launch_script(pegasus_script, identifier="start_pegasus")
print(f"Launched start_pegasus.py with PID: {pegasus_process.pid}")