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


PID_FILE = "arcade_station_image.pid"  # Ensure this matches the path in display_image.py

def kill_image_process():
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
            try:
                # Use psutil to terminate the process on Windows
                process = psutil.Process(pid)
                process.terminate()
                print(f"Killed process with PID: {pid}")
            except (psutil.NoSuchProcess, ProcessLookupError):
                print(f"No process found with PID: {pid}")
        os.remove(PID_FILE)

# kill_processes_from_toml('processes_to_kill.toml')
kill_image_process()
display_image_from_config()
start_pegasus()