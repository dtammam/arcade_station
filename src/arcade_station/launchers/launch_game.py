"""
Game Launcher Module for Arcade Station.

This module handles the launching of games from the Arcade Station frontend.
It provides functionality to launch games with appropriate settings, manage
process priorities, handle window focus, and display game-specific artwork.

The launcher supports various game types and platforms, with special handling
for different operating systems. It also manages the lifecycle of the Pegasus
frontend during game launches.
"""

import sys
import os
import subprocess
import logging
import time
import ctypes
import psutil
import platform

# Add the parent directory of 'arcade_station' to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from arcade_station.core.common.core_functions import (
    load_game_config, 
    load_mame_config, 
    kill_pegasus, 
    load_toml_config,
    kill_process_by_identifier,
    log_message,
    start_process_with_powershell,
    run_powershell_script
)
from arcade_station.core.common.light_control import launch_mame_lights
from arcade_station.core.common.display_image import display_image

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def set_process_priority(pid, priority="high"):
    """
    Set the priority of a process to improve performance and responsiveness.
    
    Adjusts the operating system's scheduling priority for the specified process,
    which can help ensure games receive appropriate CPU time and resources.
    
    Args:
        pid (int): Process ID of the target process.
        priority (str): Priority level to set. Options are "low", "below_normal",
                       "normal", "above_normal", "high", or "realtime".
                       Defaults to "high".
    
    Returns:
        bool: True if priority was set successfully, False otherwise.
        
    Note:
        Setting a process to "realtime" priority can cause system instability
        and should be used with caution.
    """
    try:
        if not pid:
            return False
            
        process = psutil.Process(pid)
        
        # Map priority levels to psutil constants
        priority_map = {
            "low": psutil.IDLE_PRIORITY_CLASS,
            "below_normal": psutil.BELOW_NORMAL_PRIORITY_CLASS,
            "normal": psutil.NORMAL_PRIORITY_CLASS,
            "above_normal": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
            "high": psutil.HIGH_PRIORITY_CLASS,
            "realtime": psutil.REALTIME_PRIORITY_CLASS
        }
        
        # Set priority if valid level
        if priority in priority_map:
            process.nice(priority_map[priority])
            log_message(f"Set process {pid} priority to {priority}", "GAME")
            return True
            
        return False
    except Exception as e:
        log_message(f"Failed to set process priority: {e}", "GAME")
        return False

def force_window_focus():
    """
    Force Windows to refresh window focus by simulating Alt key press.
    
    Uses the Windows API to simulate pressing and releasing the Alt key,
    which forces Windows to reevaluate window focus. This can help ensure
    that the game window properly receives focus after launching.
    
    Returns:
        None
        
    Note:
        This function is Windows-specific and will fail on other operating systems.
        It uses ctypes to directly access the Windows API.
    """
    try:
        # Define Windows API constants
        ALT_KEY = 0x12
        KEYEVENTF_KEYUP = 0x0002
        
        # Press and release the Alt key to force Windows to refresh focus
        ctypes.windll.user32.keybd_event(ALT_KEY, 0, 0, 0)  # Alt press
        time.sleep(0.1)
        ctypes.windll.user32.keybd_event(ALT_KEY, 0, KEYEVENTF_KEYUP, 0)  # Alt release
        log_message("Forced window focus refresh", "GAME")
    except Exception as e:
        log_message(f"Failed to force window focus: {e}", "GAME")

def launch_game(game_name):
    """
    Launch a game from the Arcade Station configuration.
    
    This is the main function for launching games from the Arcade Station frontend.
    It handles different game types (MAME ROMs, standalone executables, etc.),
    displays appropriate marquee/banner images, manages the Pegasus frontend
    lifecycle, and sets up the environment for optimal game performance.
    
    Args:
        game_name (str): The name of the game to launch, as defined in the
                        installed_games.toml configuration file.
    
    Returns:
        None
        
    Note:
        This function will:
        1. Display a game-specific banner/marquee if configured
        2. Kill the Pegasus frontend if necessary
        3. Launch the game with appropriate parameters
        4. Set process priority for better performance
        5. Handle platform-specific window focus issues
    """
    # Log game launch attempt with timestamp
    log_message(f"Attempting to launch game: {game_name}", "GAME_LAUNCH")
    
    # Load game configuration
    config = load_game_config()
    game_config = config['games'].get(game_name, {})    
    # Check if dynamic marquee is enabled
    display_config = load_toml_config('display_config.toml')
    dynamic_marquee_enabled = display_config.get('dynamic_marquee', {}).get('enabled', False)
    
    # Display banner if configured
    if dynamic_marquee_enabled and 'banner' in game_config:
        banner_path = game_config['banner']
        if banner_path and os.path.exists(banner_path):
            logging.debug(f"Displaying banner: {banner_path}")
            kill_process_by_identifier("marquee_image")  # Use standardized identifier
            display_image(banner_path, display_config['display']['background_color'])
    
    # Existing logic to launch the game...
    if game_name in config['games']:
        game_config = config['games'][game_name]
        if isinstance(game_config, dict) and 'rom' in game_config:
            # MAME game logic
            rom = game_config['rom']
            state = game_config.get('state', '')
            log_message(f"Launching MAME game - ROM: {rom}, State: {state}", "GAME_LAUNCH")
            mame_script = os.path.join(os.path.dirname(__file__), '..', 'core', 'windows', 'start_mame.ps1')
            
            # Log the full script path for troubleshooting
            log_message(f"MAME script path: {os.path.abspath(mame_script)}", "GAME_LAUNCH")
            
            # Load MAME configuration
            mame_config = load_mame_config()
            log_message(f"Loaded MAME config: {mame_config}", "GAME")
            executable_path = mame_config['mame']['executable_path']
            executable = mame_config['mame']['executable']
            ini_path = mame_config['mame']['ini_path']
            
            # Launch MAME lights if configured
            launch_mame_lights()
            
            # Pass parameters to PowerShell script
            process = run_powershell_script(
                script_path=mame_script,
                params={
                    "ROM": rom, 
                    "State": state,
                    "ExecutablePath": executable_path, 
                    "Executable": executable, 
                    "IniPath": ini_path
                }
            )
            
            # Set priority and force focus
            if process:
                set_process_priority(process.pid, "high")
                log_message(f"Successfully launched MAME game: {rom}", "GAME_LAUNCH")
            else:
                log_message(f"Failed to get process handle for MAME game: {rom}", "GAME_LAUNCH")
            
            # Give process time to start and then force window focus
            time.sleep(2)
            force_window_focus()
            
            # Kill Pegasus after launching the game
            kill_pegasus()
        else:
            # Binary game logic
            game_path = game_config.get('path', '') if isinstance(game_config, dict) else game_config
            if game_path and os.path.exists(game_path):
                log_message(f"Launching binary game: {game_path}", "GAME_LAUNCH")
                try:
                    # Change the working directory to the directory of the executable
                    game_dir = os.path.dirname(game_path)
                    
                    # Check if we're on Windows and use PowerShell if so
                    if platform.system() == "Windows":
                        # Log detailed info about game launch
                        log_message(f"Launching via PowerShell - Path: {game_path}, Dir: {game_dir}", "GAME_LAUNCH")
                        
                        # Use PowerShell to start the process
                        success = start_process_with_powershell(
                            file_path=game_path,
                            working_dir=game_dir
                        )
                        
                        if not success:
                            log_message("Failed to start game with PowerShell", "GAME_LAUNCH")
                            raise Exception("Failed to start game with PowerShell")
                        else:
                            log_message(f"Successfully launched game via PowerShell: {game_path}", "GAME_LAUNCH")
                    else:
                        # For non-Windows platforms, use the original approach
                        log_message(f"Launching via subprocess on non-Windows platform", "GAME_LAUNCH")
                        os.chdir(game_dir)
                        process = subprocess.Popen(game_path)
                        # Set priority
                        set_process_priority(process.pid, "high")
                        log_message(f"Successfully launched game via subprocess: {game_path}", "GAME_LAUNCH")
                    
                    # Give process time to start and then force window focus
                    time.sleep(2)
                    force_window_focus()
                    
                except Exception as e:
                    log_message(f"Failed to launch game: {e}", "GAME_LAUNCH")
                
                # Kill Pegasus after launching the game
                kill_pegasus()
            else:
                log_message(f"Game path not found or invalid: {game_path}", "GAME_LAUNCH")
    else:
        log_message(f"Game '{game_name}' not found in configuration.", "GAME_LAUNCH")

if __name__ == "__main__":
    # Check if a game name was provided as a command-line argument
    if len(sys.argv) > 1:
        game_name = sys.argv[1]
        launch_game(game_name)
    else:
        log_message("No game name provided. Usage: python launch_game.py <game_name>", "GAME")