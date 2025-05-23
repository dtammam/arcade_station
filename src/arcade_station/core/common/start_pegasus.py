"""
Launch the Pegasus Frontend Application.

This utility script starts the Pegasus frontend, which serves as the main
user interface for the Arcade Station system. It provides access to the
game library, system settings, and other features.

The script uses the start_pegasus function from core_functions.py, which
determines the appropriate Pegasus binary for the current platform and
launches it. This ensures that the correct version of Pegasus is started
regardless of the operating system.
"""

import sys
import os
# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

from arcade_station.core.common.core_functions import start_pegasus

if __name__ == "__main__":
    """
    Main entry point for the script.
    
    When run directly, this script will:
    1. Import the start_pegasus function from core_functions
    2. Execute the function to launch the Pegasus frontend
    3. Handle any platform-specific initialization automatically
    
    Returns:
        None. The Pegasus frontend will be launched as a separate process.
    """
    start_pegasus() 