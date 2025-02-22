import sys
import os
import subprocess

# Add the parent directory of 'arcade_station' to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from arcade_station.core.common.core_functions import load_game_config, load_mame_config, kill_pegasus
from arcade_station.core.common.light_control import launch_mame_lights

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
            game_path = game_config
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