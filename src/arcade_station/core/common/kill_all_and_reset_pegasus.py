import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
from arcade_station.core.common.core_functions import *
from arcade_station.core.common.light_control import reset_lights
from arcade_station.core.common.display_image import display_image_from_config


kill_processes_from_toml('processes_to_kill.toml')
reset_lights()
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