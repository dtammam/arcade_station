"""
Terminate the Pegasus Frontend Process.

This simple utility script terminates any running instances of the Pegasus
frontend application. It's used when games need to be launched in fullscreen
mode or when the system needs to be shut down cleanly.

The script uses the kill_pegasus function from core_functions.py, which
identifies and terminates Pegasus processes in a platform-appropriate way.
This ensures that Pegasus is properly closed before other operations that
might conflict with it.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
from arcade_station.core.common.core_functions import kill_pegasus, log_message

def main():
    """
    Main entry point for the Pegasus termination script.
    
    Calls the kill_pegasus function to terminate any running instances
    of the Pegasus frontend application.
    
    Returns:
        None
    """
    log_message("Terminating Pegasus frontend", "KILL")
    kill_pegasus()

if __name__ == "__main__":
    main() 