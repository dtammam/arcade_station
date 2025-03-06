"""
Reset Arcade Station Environment and Restart Pegasus Frontend.

This script performs a complete reset of the Arcade Station environment and
restarts the Pegasus frontend. It's used as a recovery mechanism when the
system needs to be returned to a clean state, such as after exiting a game
or when encountering issues.

The script performs the following actions:
1. Kills all running processes defined in the processes_to_kill.toml file
2. Resets any active lighting effects
3. Terminates specific processes like LightsTest and marquee image display
4. Displays the default marquee image if dynamic marquee is enabled
5. Restarts the Pegasus frontend

This script can be triggered by keyboard shortcuts or called by other
components of the Arcade Station system.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
from arcade_station.core.common.core_functions import (
    kill_processes_from_toml,
    kill_process_by_identifier,
    load_toml_config,
    log_message,
    start_pegasus
)
from arcade_station.core.common.light_control import reset_lights, kill_specific_lights_process
from arcade_station.core.common.display_image import display_image_from_config

# Kill all processes that might interfere with a clean restart
kill_processes_from_toml('processes_to_kill.toml')
reset_lights()
# Only kill LightsTest if it's still running, not mame2lit
kill_specific_lights_process("LightsTest")
kill_process_by_identifier("marquee_image")
kill_process_by_identifier("start_pegasus")

# Check if dynamic marquee is enabled before displaying an image
config = load_toml_config('display_config.toml')
dynamic_marquee_enabled = config.get('dynamic_marquee', {}).get('enabled', False)

if dynamic_marquee_enabled:
    # Only display the default image if dynamic marquee is enabled
    process = display_image_from_config(use_default=True)
    log_message("Started marquee image display process", "MENU")
else:
    log_message("Dynamic marquee is disabled, not showing an image", "MENU")

start_pegasus() 