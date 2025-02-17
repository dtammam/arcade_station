import sys
import os
import tomllib
import subprocess
# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Image launch
from core.common.display_image import *

# Load game configuration from TOML file
def load_game_config():
    # Determine the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Calculate the absolute path to the config file
    config_path = os.path.join(script_dir, '..', '..', '..', 'config', 'installed_games.toml')
    
    with open(config_path, 'rb') as f:
        return tomllib.load(f)

if __name__ == "__main__":
    # Check for command-line argument
    if len(sys.argv) < 2:
        print("No game specified.")
        sys.exit(1)

    game_name = sys.argv[1]

    print(f"Received arguments: {sys.argv}")  # Debugging line
    print(f"Looking for game: {game_name}")  # Debugging line

    # Load game configuration
    config = load_game_config()
    game_path = config['games'].get(game_name, '')

    print(f"Resolved game path: {game_path}")  # Debugging line

    if game_path and os.path.exists(game_path):
        # Launch the game
        subprocess.Popen(game_path)
    else:
        print(f"Game path for '{game_name}' not found or not specified.")