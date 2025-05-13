"""
Kill all Arcade Station processes.

This script kills all running processes defined in the processes_to_kill.toml file
and handles specific processes like LightsTest and marquee image display.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
from arcade_station.core.common.core_functions import (
    kill_processes_from_toml,
    kill_process_by_identifier,
    log_message
)
from arcade_station.core.common.light_control import reset_lights, kill_specific_lights_process

def main():
    # Kill all processes that might interfere
    log_message("Killing processes", "RESET")
    kill_processes_from_toml('processes_to_kill.toml')
    
    log_message("Resetting lights", "RESET")
    reset_lights()
    
    log_message("Killing specific lights process", "RESET")
    kill_specific_lights_process("LightsTest")
    
    log_message("Killing marquee image process", "RESET")
    kill_process_by_identifier("marquee_image")

if __name__ == "__main__":
    main() 