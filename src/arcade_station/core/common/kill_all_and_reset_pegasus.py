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
import subprocess
import time

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

def main():
    # Kill all processes that might interfere with a clean restart
    log_message("Killing processes that might interfere with a clean restart", "RESET")
    kill_processes_from_toml('processes_to_kill.toml')
    
    log_message("Resetting lights", "RESET")
    reset_lights()
    
    # Only kill LightsTest if it's still running, not mame2lit
    log_message("Killing specific lights process", "RESET")
    kill_specific_lights_process("LightsTest")
    
    log_message("Killing marquee image process", "RESET")
    kill_process_by_identifier("marquee_image")
    
    log_message("Killing previous pegasus start process", "RESET")
    kill_process_by_identifier("start_pegasus")

    # Check if dynamic marquee is enabled before displaying an image
    log_message("Loading display configuration", "RESET")
    config = load_toml_config('display_config.toml')
    dynamic_marquee_enabled = config.get('dynamic_marquee', {}).get('enabled', False)

    if dynamic_marquee_enabled:
        # Only display the default image if dynamic marquee is enabled
        log_message("Starting marquee image display process", "RESET")
        process = display_image_from_config(use_default=True)
        log_message("Started marquee image display process", "MENU")
    else:
        log_message("Dynamic marquee is disabled, not showing an image", "MENU")

    # Try to start Pegasus using the core_functions method
    log_message("Attempting to start Pegasus", "RESET")
    pegasus_started = start_pegasus()
    
    # If start_pegasus failed, try alternative methods
    if not pegasus_started:
        log_message("Failed to start Pegasus with primary method, trying alternatives", "RESET")
        
        # Alternative 1: Try to find and run Pegasus using installed_games.toml
        try:
            log_message("Trying to locate Pegasus executable from configuration", "RESET")
            config = load_toml_config('installed_games.toml')
            
            # Determine OS and get the appropriate binary name
            os_type = os.name
            if os_type == 'nt':  # Windows
                binary_name = config.get('pegasus', {}).get('windows_binary', 'pegasus-fe_windows.exe')
            elif os_type == 'posix' and sys.platform == 'darwin':  # macOS
                binary_name = config.get('pegasus', {}).get('mac_binary', 'pegasus-fe_mac')
            else:  # Linux or other Unix-like
                binary_name = config.get('pegasus', {}).get('linux_binary', 'pegasus-fe_linux')
            
            # Try to find the binary in common locations
            potential_locations = [
                os.path.join(os.path.dirname(sys.executable), 'pegasus-fe'),
                os.path.join(os.path.dirname(sys.executable), '..', 'pegasus-fe'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'pegasus-fe'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'pegasus-fe')
            ]
            
            pegasus_path = None
            for location in potential_locations:
                potential_path = os.path.join(location, binary_name)
                if os.path.exists(potential_path):
                    pegasus_path = potential_path
                    break
            
            if pegasus_path:
                log_message(f"Found Pegasus at: {pegasus_path}", "RESET")
                log_message(f"Attempting to launch Pegasus from: {pegasus_path}", "RESET")
                
                # Get the working directory (the directory containing the binary)
                working_dir = os.path.dirname(pegasus_path)
                
                # Try to launch the process
                if os_type == 'nt':  # Windows
                    process = subprocess.Popen(
                        pegasus_path,
                        shell=True,
                        cwd=working_dir,
                        creationflags=subprocess.CREATE_NEW_CONSOLE
                    )
                else:  # macOS and Linux
                    process = subprocess.Popen(
                        [pegasus_path],
                        cwd=working_dir
                    )
                
                # Wait a bit to see if it started
                time.sleep(2)
                if process.poll() is None:
                    log_message("Pegasus successfully started with alternative method", "RESET")
                else:
                    log_message(f"Pegasus process exited immediately with code: {process.returncode}", "RESET")
            else:
                log_message("Could not find Pegasus executable in common locations", "RESET")
                
        except Exception as e:
            log_message(f"Error in alternative Pegasus launch: {e}", "RESET")
            import traceback
            log_message(traceback.format_exc(), "RESET")

if __name__ == "__main__":
    main() 