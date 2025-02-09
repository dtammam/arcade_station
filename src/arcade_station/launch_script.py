import sys
import os
import threading
import multiprocessing
import subprocess
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt
import argparse
from arcade_station.core.common.core_functions import launch_script

def main():
    parser = argparse.ArgumentParser(
        description="Launch a Python script with a configured virtual environment."
    )
    parser.add_argument(
        "script",
        help="Path to the Python script to launch."
    )
    parser.add_argument(
        "--identifier",
        default=None,
        help="Optional identifier to pass to the script (e.g., '--identifier=open_image')."
    )
    args = parser.parse_args()

    # Resolve script path to an absolute path.
    script_path = os.path.abspath(args.script)
    if not os.path.exists(script_path):
        print(f"Error: script not found at {script_path}")
        sys.exit(1)

    # Call the central launch function provided in core_functions.
    process = launch_script(script_path, identifier=args.identifier)
    print(f"Launched process with PID: {process.pid}")

if __name__ == "__main__":
    main()