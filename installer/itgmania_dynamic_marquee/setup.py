"""
Setup ITGMania Dynamic Marquee Integration

This script sets up the integration between Arcade Station and ITGMania by:
1. Copying shim files to the ITGMania installation
2. Configuring the display_config.toml with the correct log file path
"""

import os
import sys
import shutil
import platform
import datetime
from pathlib import Path
import tomllib  # Standard library in Python 3.11+

# Add the root directory to the Python path
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Define fallback functions in case arcade_station module is not available
def fallback_log_message(message, category="INFO"):
    """
    Fallback logging function if arcade_station is not available.
    
    Args:
        message (str): The message to log.
        category (str): The log category.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{category}] {message}")

def fallback_load_toml_config(config_path):
    """
    Fallback function to load TOML config if arcade_station is not available.
    
    Args:
        config_path (str): Path to the TOML config file.
        
    Returns:
        dict: Parsed TOML config.
    """
    config_path = Path(config_path)
    
    # Check if the path is relative and not absolute
    if not config_path.is_absolute():
        # First try relative to the root directory
        root_config = ROOT_DIR / config_path
        if root_config.exists():
            config_path = root_config
        # Then try relative to the config directory
        else:
            config_dir = ROOT_DIR / "config"
            if config_dir.exists():
                config_dir_path = config_dir / config_path
                if config_dir_path.exists():
                    config_path = config_dir_path
    
    # Load the TOML file
    try:
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    except Exception as e:
        print(f"Error loading config from {config_path}: {e}")
        return {}

# Try to import from arcade_station, but use fallbacks if not available
try:
    from arcade_station.core.common.core_functions import (
        load_toml_config,
        log_message
    )
    print("Successfully imported arcade_station modules.")
except ImportError:
    print("Warning: Could not import arcade_station modules. Using fallback functions.")
    load_toml_config = fallback_load_toml_config
    log_message = fallback_log_message


def get_itgmania_install_path():
    """
    Ask the user for the ITGMania installation path and validate it.
    
    Returns:
        Path: The validated ITGMania installation path.
    """
    while True:
        print("\n===== ITGMania Integration Setup =====")
        print("This script will configure your ITGMania installation to work with Arcade Station's dynamic marquee.")
        
        default_paths = {
            "windows": r"C:\Games\ITGmania",
            "darwin": "/Applications/ITGmania",
            "linux": os.path.expanduser("~/ITGmania")
        }
        
        system = platform.system().lower()
        if system in default_paths:
            default_path = default_paths[system]
        else:
            default_path = "ITGmania"
        
        itgmania_path = input(f"\nEnter the path to your ITGMania installation [default: {default_path}]: ")
        
        if not itgmania_path:
            itgmania_path = default_path
        
        install_path = Path(itgmania_path)
        
        # Validate the path
        if not install_path.exists():
            print(f"Error: The path {install_path} does not exist.")
            retry = input("Would you like to try again? (y/n): ").lower()
            if retry != 'y':
                sys.exit(1)
            continue
        
        # Check if this looks like an ITGMania installation
        if not (install_path / "Themes").exists():
            print(f"Warning: This doesn't appear to be a valid ITGMania installation (no Themes folder found).")
            confirm = input("Continue anyway? (y/n): ").lower()
            if confirm != 'y':
                continue
        
        return install_path


def copy_shim_files(itgmania_path):
    """
    Copy the shim files to the ITGMania installation.
    
    Args:
        itgmania_path (Path): The path to the ITGMania installation.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Source paths - using the new installer directory structure
        source_base_dir = SCRIPT_DIR / "shims"
        
        # Destination paths
        dest_base_dir = itgmania_path / "Themes" / "Simply Love" / "BGAnimations"
        
        # Directories to copy contents from
        directories_to_copy = [
            "ScreenGameplay overlay",
            "ScreenSelectMusic overlay"
        ]
        
        # Check if destination directories exist
        for dir_name in directories_to_copy:
            dest_dir = dest_base_dir / dir_name
            if not dest_dir.exists():
                log_message(f"Destination directory {dest_dir} does not exist.", "SETUP")
                print(f"Error: Required directory {dir_name} not found in ITGMania installation.")
                return False
        
        # Copy files
        for dir_name in directories_to_copy:
            source_dir = source_base_dir / dir_name
            dest_dir = dest_base_dir / dir_name
            
            print(f"Copying files to {dest_dir}...")
            
            for file_path in source_dir.glob('*'):
                if file_path.is_file():
                    dest_file = dest_dir / file_path.name
                    # Always overwrite existing files
                    shutil.copy2(file_path, dest_file)
                    print(f"  - Copied {file_path.name}")
        
        return True
    
    except Exception as e:
        log_message(f"Error copying shim files: {str(e)}", "SETUP")
        print(f"Error: Failed to copy shim files: {str(e)}")
        return False


def determine_log_file_path(itgmania_path):
    """
    Determine the log file path based on whether ITGMania is in portable mode.
    
    Args:
        itgmania_path (Path): The path to the ITGMania installation.
    
    Returns:
        str: The path to the log file.
    """
    # Check if portable.txt exists
    if (itgmania_path / "portable.txt").exists():
        # Portable mode
        log_file_path = itgmania_path / "Save" / "CurrentSongInfo.log"
        
        # Ensure Save directory exists
        save_dir = itgmania_path / "Save"
        if not save_dir.exists():
            save_dir.mkdir(parents=True)
        
        print("ITGMania is in portable mode.")
    else:
        # Non-portable mode
        if platform.system().lower() == "windows":
            appdata = os.environ.get("APPDATA", "")
            log_file_path = Path(appdata) / "ITGmania" / "Save" / "CurrentSongInfo.log"
        else:
            home = os.path.expanduser("~")
            log_file_path = Path(home) / ".itgmania" / "Save" / "CurrentSongInfo.log"
        
        # Ensure Save directory exists
        save_dir = log_file_path.parent
        if not save_dir.exists():
            save_dir.mkdir(parents=True)
        
        print("ITGMania is in non-portable mode.")
    
    # Create an empty log file if it doesn't exist
    if not log_file_path.exists():
        log_file_path.touch()
        print(f"Created empty log file at {log_file_path}")
    
    return str(log_file_path)


def update_config(log_file_path):
    """
    Update the display_config.toml with the ITGMania log file path.
    
    Args:
        log_file_path (str): The path to the ITGMania log file.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Find the config file path
        config_path = ROOT_DIR / "config" / "display_config.toml"
        
        if not config_path.exists():
            log_message(f"Config file {config_path} does not exist.", "SETUP")
            print(f"Error: Config file {config_path} not found.")
            return False
        
        # Load the config file using tomllib
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
        
        # Convert backslashes to forward slashes for TOML-friendliness
        log_file_path = log_file_path.replace('\\', '/')
        
        # Update the config
        if "dynamic_marquee" not in config:
            config["dynamic_marquee"] = {}
        
        # Always overwrite the settings
        config["dynamic_marquee"]["enabled"] = True
        config["dynamic_marquee"]["itgmania_display_enabled"] = True
        config["dynamic_marquee"]["itgmania_display_file_path"] = log_file_path
        
        # Save the updated config - tomllib doesn't provide a writer, so we write manually
        with open(config_path, "w", encoding="utf-8") as f:
            # Write each section with proper formatting
            for section_idx, (section, values) in enumerate(config.items()):
                f.write(f"[{section}]\n")
                
                for key_idx, (key, value) in enumerate(values.items()):
                    if isinstance(value, bool):
                        value_str = str(value).lower()
                    elif isinstance(value, str):
                        value_str = f'"{value}"'
                    else:
                        value_str = str(value)
                    
                    f.write(f"{key} = {value_str}\n")
                
                # Only add newline between sections (not after the last section)
                if section_idx < len(config) - 1:
                    f.write("\n")
        
        print(f"Updated display_config.toml with log file path: {log_file_path}")
        return True
    
    except Exception as e:
        log_message(f"Error updating config: {str(e)}", "SETUP")
        print(f"Error: Failed to update config: {str(e)}")
        return False


def main():
    """
    Main function to set up ITGMania integration.
    """
    try:
        print("\n==================================================")
        print("   Arcade Station - ITGMania Integration Setup")
        print("==================================================")
        
        # Step 1: Get ITGMania installation path
        itgmania_path = get_itgmania_install_path()
        
        # Step 2: Copy shim files
        print("\nStep 1: Copying required files to ITGMania installation...")
        if not copy_shim_files(itgmania_path):
            sys.exit(1)
        
        # Step 3: Determine log file path
        print("\nStep 2: Determining log file path...")
        log_file_path = determine_log_file_path(itgmania_path)
        
        # Step 4: Update config
        print("\nStep 3: Updating configuration...")
        if not update_config(log_file_path):
            sys.exit(1)
        
        print("\n==================================================")
        print("   Setup Complete!")
        print("==================================================")
        print("ITGMania is now configured to work with Arcade Station's dynamic marquee.")
        print(f"Log file path: {log_file_path}")
        print("\nTo use this feature:")
        print("1. Make sure Arcade Station is running")
        print("2. Launch ITGMania")
        print("3. Select songs to see their banners on your marquee display")
        print("==================================================")
        
    except KeyboardInterrupt:
        print("\nSetup canceled by user.")
        sys.exit(1)
    except Exception as e:
        log_message(f"Setup failed: {str(e)}", "SETUP")
        print(f"\nError: Setup failed: {str(e)}")
        
        # Print traceback for debugging
        import traceback
        traceback.print_exc()
        
        sys.exit(1)


if __name__ == "__main__":
    main() 