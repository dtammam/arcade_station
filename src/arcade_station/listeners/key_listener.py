import sys
import os
# Add the parent directory of 'arcade_station' to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from arcade_station.core.common.core_functions import *

start_listening_to_keybinds_from_toml('key_listener.toml') 