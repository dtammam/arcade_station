"""
Keyboard Event Listener for Arcade Station.

This module sets up global keyboard shortcuts for the Arcade Station application.
It loads key bindings from a TOML configuration file and registers hotkeys that
trigger various actions when pressed, such as launching applications or killing
processes.

The listener runs in the background and monitors for configured key combinations,
allowing users to control the Arcade Station system without needing to access
the frontend directly.
"""

import sys
import os

# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from arcade_station.core.common.core_functions import start_listening_to_keybinds_from_toml

start_listening_to_keybinds_from_toml('key_listener.toml') 