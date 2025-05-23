#!/usr/bin/env python
"""
Screenshot Utility for Arcade Station.

This script provides a console-free screenshot functionality for Arcade Station.
It uses a double-wrapper approach to ensure no console windows are shown during
screenshot capture. The script:
1. Launches a wrapper script that handles the actual screenshot capture
2. Uses process identifiers for proper tracking and management
3. Exits immediately to prevent console window display

This script can be called directly or through system shortcuts, making it
suitable for keyboard hotkeys and automated capture scenarios.
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