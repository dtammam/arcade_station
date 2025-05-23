"""
Screenshot Wrapper Module for Arcade Station.

This module serves as a wrapper for the monitor_screenshot.py script,
providing a clean interface for taking screenshots without console window
visibility. It handles:
- Automatic path resolution for the screenshot script
- Process management with hidden console window
- Proper exit code propagation
"""

import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from arcade_station.core.common.core_functions import launch_script

if __name__ == "__main__":
    """
    Main entry point for the screenshot wrapper.
    
    When run directly, this script will:
    1. Locate the monitor_screenshot.py script
    2. Launch it using launch_script with hidden console
    3. Wait for completion and propagate exit code
    
    Returns:
        None. Exits with the same status code as the screenshot script.
    """
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