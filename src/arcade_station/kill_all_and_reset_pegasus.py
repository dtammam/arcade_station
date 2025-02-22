import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from arcade_station.core.common.core_functions import *
from arcade_station.core.common.light_control import reset_lights


kill_processes_from_toml('processes_to_kill.toml')
reset_lights()
kill_process_by_identifier("open_image")
kill_process_by_identifier("start_pegasus")
process = launch_script(
    r'C:/Repositories/arcade_station/src/arcade_station/open_image.py',
    identifier="open_image"
)
print(f"Launched open_image.py with PID: {process.pid}")
start_pegasus()