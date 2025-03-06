import sys
import os

# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from arcade_station.core.common.core_functions import start_listening_to_keybinds_from_toml

start_listening_to_keybinds_from_toml('key_listener.toml') 