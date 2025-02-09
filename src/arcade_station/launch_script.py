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

def launch_script(script_path, identifier=None):
    """
    Launch a Python script from your virtual environment.
    
    If an identifier is provided, it is appended as a command-line argument
    (e.g. '--identifier=open_image') so that external scripts can find this process.
    
    On Windows, the process is launched with no visible console window.
    """
    # Path to your venv's Python executable.
    # TODO: Make this dynamic.
    python_executable = r"C:/Repositories/arcade_station/.venv/Scripts/python.exe"
    
    # Build the command-line arguments.
    args = [python_executable, script_path]
    if identifier:
        args.append(f"--identifier={identifier}")
    
    # Windows-specific options: hide the console window.
    if os.name == 'nt':
        creationflags = subprocess.CREATE_NO_WINDOW
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # 0 means SW_HIDE.
    else:
        creationflags = 0
        startupinfo = None

    process = subprocess.Popen(
        args,
        creationflags=creationflags,
        startupinfo=startupinfo
    )
    return process

# Example usage:
if __name__ == '__main__':
    # Launch the script and "tag" it with an identifier.
    process = launch_script(
        r'C:/Repositories/arcade_station/src/arcade_station/open_image.py',
        identifier="open_image"  # This will appear in the process command-line.
    )