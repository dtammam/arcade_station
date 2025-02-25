import sys
import os
import subprocess
import logging

# Add the parent directory of 'arcade_station' to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from arcade_station.core.common.core_functions import (
    load_game_config, 
    load_mame_config, 
    kill_pegasus, 
    load_toml_config,
    kill_process_by_identifier,
    log_message
)
from arcade_station.core.common.light_control import launch_mame_lights
from arcade_station.core.common.display_image import display_image

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def launch_game(game_name):
    # Load game configuration
    config = load_game_config()
    game_config = config['games'].get(game_name, {})    
    # Check if dynamic marquee is enabled
    display_config = load_toml_config('display_config.toml')
    dynamic_marquee_enabled = display_config['display'].get('dynamic_marquee_enabled', False)
    
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
            log_message(f"ROM: {rom}, State: {state}", "GAME")
            mame_script = os.path.join(os.path.dirname(__file__), '..', 'core', 'windows', 'StartMAME.ps1')
            
            # Load MAME configuration
            mame_config = load_mame_config()
            log_message(f"Loaded MAME config: {mame_config}", "GAME")
            executable_path = mame_config['mame']['executable_path']
            executable = mame_config['mame']['executable']
            ini_path = mame_config['mame']['ini_path']
            
            # Launch MAME lights if configured
            launch_mame_lights()
            
            # Pass parameters to PowerShell script
            subprocess.Popen([
                'powershell.exe', '-WindowStyle', 'Hidden', '-File', mame_script,
                '-ROM', rom, '-State', state,
                '-ExecutablePath', executable_path, '-Executable', executable, '-IniPath', ini_path
            ])
            
            # Kill Pegasus after launching the game
            kill_pegasus()
        else:
            # Binary game logic
            game_path = game_config.get('path', '') if isinstance(game_config, dict) else game_config
            if game_path and os.path.exists(game_path):
                log_message(f"Launching binary game: {game_path}", "GAME")
                try:
                    # Change the working directory to the directory of the executable
                    game_dir = os.path.dirname(game_path)
                    os.chdir(game_dir)
                    
                    # Launch the game
                    subprocess.Popen(game_path)
                except Exception as e:
                    log_message(f"Failed to launch game: {e}", "GAME")
                
                # Kill Pegasus after launching the game
                kill_pegasus()
            else:
                log_message(f"Game path not found or invalid: {game_path}", "GAME")
    else:
        log_message(f"Game '{game_name}' not found in configuration.", "GAME")

if __name__ == "__main__":
    # Check if a game name was provided as a command-line argument
    if len(sys.argv) > 1:
        game_name = sys.argv[1]
        launch_game(game_name)
    else:
        log_message("No game name provided. Usage: python launch_game.py <game_name>", "GAME")