import sys
import os
import subprocess
import logging

# Add the parent directory of 'arcade_station' to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from arcade_station.core.common.core_functions import load_game_config, load_mame_config, kill_pegasus, load_toml_config
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
            display_image(banner_path, display_config['display']['background_color'])
    
    # Existing logic to launch the game...
    if game_name in config['games']:
        game_config = config['games'][game_name]
        if isinstance(game_config, dict) and 'rom' in game_config:
            # MAME game logic
            rom = game_config['rom']
            state = game_config.get('state', '')
            logging.debug(f"Launching MAME game with ROM: {rom}, State: {state}")
            mame_script = os.path.join(os.path.dirname(__file__), '..', 'core', 'windows', 'StartMAME.ps1')
            
            # Load MAME configuration
            mame_config = load_mame_config()
            logging.debug(f"Loaded MAME config: {mame_config}")
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
                logging.debug(f"Launching binary game: {game_path}")
                try:
                    # Change the working directory to the directory of the executable
                    game_dir = os.path.dirname(game_path)
                    os.chdir(game_dir)
                    
                    # Launch the game
                    subprocess.Popen(game_path, shell=True)
                except Exception as e:
                    logging.error(f"Failed to launch game: {e}")
                
                # Kill Pegasus after launching the game
                kill_pegasus()
            else:
                logging.error(f"Game path not found or invalid: {game_path}")
    else:
        logging.error(f"Game '{game_name}' not found in configuration.")

if __name__ == "__main__":
    # Check for command-line argument
    if len(sys.argv) < 2:
        print("No game specified.")
        sys.exit(1)

    game_name = sys.argv[1]
    print(f"Game name: {game_name}")  # Debugging line

    # Load game configuration
    config = load_game_config()
    print(f"Loaded game config: {config}")  # Debugging line
    game_path = config['games'].get(game_name, '')

    # Check if dynamic marquee is enabled
    display_config = load_toml_config('display_config.toml')
    dynamic_marquee_enabled = display_config['display'].get('dynamic_marquee_enabled', False)
    
    # Display banner if configured
    if dynamic_marquee_enabled and 'banner' in config['games'].get(game_name, {}):
        banner_path = config['games'][game_name]['banner']
        if banner_path and os.path.exists(banner_path):
            display_image(banner_path, display_config['display']['background_color'])

    if game_name in config['games']:
        game_config = config['games'][game_name]
        if isinstance(game_config, dict) and 'rom' in game_config:
            # MAME game logic
            rom = game_config['rom']
            state = game_config.get('state', '')
            print(f"ROM: {rom}, State: {state}")  # Debugging line
            mame_script = os.path.join(os.path.dirname(__file__), '..', 'core', 'windows', 'StartMAME.ps1')
            
            # Load MAME configuration
            mame_config = load_mame_config()
            print(f"Loaded MAME config: {mame_config}")  # Debugging line
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
                # Change the working directory to the directory of the executable
                game_dir = os.path.dirname(game_path)
                os.chdir(game_dir)
                
                # Launch the game
                subprocess.Popen(game_path)
                
                # Kill Pegasus after launching the game
                kill_pegasus()
    else:
        print(f"Game path for '{game_name}' not found or not specified.")