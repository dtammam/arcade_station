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

# Directly use display_image_from_config instead of launching open_image.py
process = display_image_from_config(use_default=True)
log_message("Started marquee image display process", "MENU")

start_pegasus() 