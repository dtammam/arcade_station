import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from arcade_station.core.common.core_functions import launch_script, log_message
from arcade_station.core.common.display_image import display_image_from_config

# Determine the current directory of this script.
base_dir = os.path.dirname(os.path.abspath(__file__))

# Construct absolute paths to the relative scripts.
listener_script = os.path.join(base_dir, "listeners", "key_listener.py")
pegasus_script = os.path.join(base_dir, "core", "common", "start_pegasus.py")

# Launch the key_listener.py script with the appropriate identifier.
listener_process = launch_script(listener_script, identifier="key_listener")
log_message(f"Launched key_listener.py with PID: {listener_process.pid}", "MENU")

# Display default image using the standardized approach
default_image_process = display_image_from_config(use_default=True)
log_message(f"Launched default image display with standardized process", "BANNER")

# Launch the start_pegasus.py script with its identifier.
pegasus_process = launch_script(pegasus_script, identifier="start_pegasus")
log_message(f"Launched start_pegasus.py with PID: {pegasus_process.pid}", "GAME")