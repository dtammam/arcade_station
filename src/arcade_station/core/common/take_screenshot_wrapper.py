#!/usr/bin/env python
import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from arcade_station.core.common.core_functions import launch_script

if __name__ == "__main__":
    # Get the path to the screenshot script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    screenshot_script = os.path.join(script_dir, "monitor_screenshot.py")
    
    # Launch the screenshot script using the launch_script function
    # This will automatically hide the console window
    process = launch_script(
        script_path=screenshot_script,
        identifier="screenshot",
    )
    
    # Wait for the process to complete (optional)
    # If you want this to be non-blocking, you can remove these lines
    process.wait()
    sys.exit(process.returncode) 