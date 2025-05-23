#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Arcade Station Installer Launcher

This launcher script starts the Arcade Station installer without showing a console window.
The .pyw extension is recognized by Windows to run Python scripts without a console.
"""
import os
import sys
import subprocess

def main():
    """Launch the Arcade Station installer as a subprocess without a console window.

    Finds the main.py script in the same directory and runs it using the current Python interpreter.
    """
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the main.py file
    main_script = os.path.join(script_dir, "main.py")
    
    # Build the command to run the installer
    # We run it as a subprocess to ensure the .pyw extension's functionality
    cmd = [sys.executable, main_script]
    
    # Launch the installer
    subprocess.Popen(cmd)

if __name__ == "__main__":
    main() 