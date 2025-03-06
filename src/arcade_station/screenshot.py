#!/usr/bin/env python
"""
Screenshot utility script

This script takes a screenshot without showing a console window.
It can be called directly or through shortcuts.
"""
import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from arcade_station.core.common.core_functions import launch_script

if __name__ == "__main__":
    # Get the path to the screenshot wrapper script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    wrapper_script = os.path.join(script_dir, "core", "common", "take_screenshot_wrapper.py")
    
    # Launch the wrapper script
    # This is a double-wrapper approach that ensures no console windows are shown
    process = launch_script(
        script_path=wrapper_script,
        identifier="screenshot_launcher",
    )
    
    # Exit immediately without waiting
    # This ensures this script terminates quickly and doesn't show a console
    sys.exit(0) 