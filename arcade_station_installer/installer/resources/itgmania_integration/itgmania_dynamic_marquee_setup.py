"""
Setup ITGMania Dynamic Marquee Integration

This script sets up the integration between Arcade Station and ITGMania by:
1. Copying module files to the ITGMania installation
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
ROOT_DIR = SCRIPT_DIR.parent.parent.parent.parent
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
        fallback_log_message(f"Error loading config from {config_path}: {e}", "ERROR")
        return {}

# Try to import from arcade_station, but use fallbacks if not available
try:
    from arcade_station.core.common.core_functions import (
        load_toml_config,
        log_message
    )
    log_message("Successfully imported arcade_station modules.", "SETUP")
except ImportError:
    fallback_log_message("Warning: Could not import arcade_station modules. Using fallback functions.", "SETUP")
    load_toml_config = fallback_load_toml_config
    log_message = fallback_log_message


def validate_itgmania_path(path):
    """
    Validate that the provided path exists and looks like an ITGMania installation.
    If the path is to an executable, it will check the parent directories for a Themes folder.
    
    Args:
        path (Path): The path to validate.
        
    Returns:
        bool: True if valid, False otherwise.
        Path: The corrected base path to the ITGMania installation.
    """
    if not path.exists():
        log_message(f"Error: The path {path} does not exist.", "SETUP")
        return False, path
    
    # If the path is to a file (executable), navigate up to find the ITGMania base directory
    base_path = path
    if path.is_file():
        log_message(f"Path points to a file, looking for ITGMania base directory...", "SETUP")
        # The executable is typically in a Program subdirectory, so we need to go up at least one level
        parent_dir = path.parent
        
        # First try the immediate parent directory (Program directory)
        if (parent_dir / "Themes").exists():
            log_message(f"Found Themes directory at {parent_dir}", "SETUP")
            return True, parent_dir
        
        # Then try one level up (ITGMania root)
        root_dir = parent_dir.parent
        if (root_dir / "Themes").exists():
            log_message(f"Found Themes directory at {root_dir}", "SETUP")
            return True, root_dir
        
        # If we still haven't found it, check two levels up (unusual but possible)
        grandparent_dir = root_dir.parent
        if (grandparent_dir / "Themes").exists():
            log_message(f"Found Themes directory at {grandparent_dir}", "SETUP")
            return True, grandparent_dir
        
        log_message(f"Warning: Could not find a Themes directory in parent directories of {path}.", "SETUP")
        return False, path
    
    # If the path is already a directory, check if it has a Themes subdirectory
    if (base_path / "Themes").exists():
        log_message(f"Valid ITGMania installation found at {base_path}", "SETUP")
        return True, base_path
    
    # Check if the parent directory has a Themes subdirectory (in case we're in a subdirectory)
    parent_dir = base_path.parent
    if (parent_dir / "Themes").exists():
        log_message(f"Found Themes directory at parent directory {parent_dir}", "SETUP")
        return True, parent_dir
    
    log_message(f"Warning: The path {path} doesn't appear to be a valid ITGMania installation (no Themes folder found).", "SETUP")
    return False, path


def copy_shim_files(itgmania_path):
    """
    Copy the module file to the appropriate ITGMania location.
    
    Checks if ITGMania is running in portable mode (has Portable.ini) and installs
    to the appropriate location - either the install directory or AppData.
    
    Args:
        itgmania_path (Path): The path to the ITGMania installation.
    
    Returns:
        bool: True if successful, False otherwise.
        tuple: (dest_file, dest_image, is_portable) - Destination file paths and portable mode status
    """
    try:
        # Source paths for the module files
        source_lua = SCRIPT_DIR / "ArcadeStationMarquee.lua"
        source_png = SCRIPT_DIR / "simply-love.png"
        
        if not source_lua.exists():
            log_message(f"Module file {source_lua} does not exist.", "SETUP")
            log_message(f"Error: Module file {source_lua} not found.", "ERROR")
            return False, (None, None, False)
            
        if not source_png.exists():
            log_message(f"Fallback image {source_png} does not exist.", "SETUP")
            log_message(f"Warning: Fallback image {source_png} not found. Will use default theme image.", "WARNING")
        
        # Check if ITGMania is running in portable mode
        portable_ini = itgmania_path / "Portable.ini"
        is_portable = portable_ini.exists()
        
        if is_portable:
            log_message("Detected ITGMania running in portable mode", "SETUP")
            log_message("Detected portable mode (Portable.ini found). Installing to the local installation directory.", "SETUP")
            
            # Use local install directory
            dest_dir = itgmania_path / "Themes" / "Simply Love" / "Modules"
        else:
            log_message("ITGMania is running in standard mode (using AppData)", "SETUP")
            log_message("Standard installation detected. Installing to the user AppData directory.", "SETUP")
            
            # Use AppData location
            system = platform.system().lower()
            if system == "windows":
                # Windows AppData path
                appdata_dir = Path(os.path.expandvars("%APPDATA%")) / "ITGmania"
            elif system == "darwin":
                # macOS preferences directory
                appdata_dir = Path.home() / "Library" / "Preferences" / "ITGmania"
            elif system == "linux":
                # Linux config directory
                appdata_dir = Path.home() / ".itgmania"
            else:
                # Fallback to a directory next to the installation
                appdata_dir = itgmania_path / "AppData"
                
            dest_dir = appdata_dir / "Themes" / "Simply Love" / "Modules"
            
        # Create the Modules directory if it doesn't exist
        if not dest_dir.exists():
            log_message(f"Creating Modules directory at {dest_dir}", "SETUP")
            dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy the module file
        dest_lua = dest_dir / "ArcadeStationMarquee.lua"
        shutil.copy2(source_lua, dest_lua)
        log_message(f"Copied module file to {dest_lua}", "SETUP")
        
        # Copy the banner image if it exists
        dest_png = None
        if source_png.exists():
            dest_png = dest_dir / "simply-love.png"
            shutil.copy2(source_png, dest_png)
            log_message(f"Copied banner image to {dest_png}", "SETUP")
            
            # Create a config file with the banner path for the Lua script
            config_path = dest_dir / "ArcadeStationMarquee.config"
            with open(config_path, 'w') as f:
                f.write(str(dest_png).replace('\\', '\\\\'))
            log_message(f"Created config file with banner path at {config_path}", "SETUP")
        
        return True, (dest_lua, dest_png, is_portable)
    
    except Exception as e:
        log_message(f"Error copying module files: {str(e)}", "SETUP")
        log_message(f"Error: Failed to copy module files: {str(e)}", "ERROR")
        return False, (None, None, False)


def determine_log_file_path(itgmania_path, dest_file=None, is_portable=False):
    """
    Determine the log file path where the module will write its output.
    
    Args:
        itgmania_path (Path): The path to the ITGMania installation.
        dest_file (Path, optional): The destination file path of the Lua module.
        is_portable (bool): Whether ITGMania is running in portable mode.
    
    Returns:
        str: The path to the log file.
    """
    if dest_file:
        # If we have the destination file path, use that directory
        log_file_path = dest_file.parent / "ArcadeStationMarquee.log"
        log_message(f"Using log file path based on module location: {log_file_path}", "SETUP")
    else:
        # Determine based on portable mode
        if is_portable:
            # Portable mode - use the installation directory
            log_file_path = itgmania_path / "Themes" / "Simply Love" / "Modules" / "ArcadeStationMarquee.log"
            log_message(f"Using portable mode log path: {log_file_path}", "SETUP")
        else:
            # Standard mode - use AppData
            system = platform.system().lower()
            if system == "windows":
                appdata_dir = Path(os.path.expandvars("%APPDATA%")) / "ITGmania"
                log_file_path = appdata_dir / "Themes" / "Simply Love" / "Modules" / "ArcadeStationMarquee.log"
            elif system == "darwin":
                appdata_dir = Path.home() / "Library" / "Preferences" / "ITGmania"
                log_file_path = appdata_dir / "Themes" / "Simply Love" / "Modules" / "ArcadeStationMarquee.log"
            elif system == "linux":
                appdata_dir = Path.home() / ".itgmania"
                log_file_path = appdata_dir / "Themes" / "Simply Love" / "Modules" / "ArcadeStationMarquee.log"
            else:
                appdata_dir = itgmania_path / "AppData"
                log_file_path = appdata_dir / "Themes" / "Simply Love" / "Modules" / "ArcadeStationMarquee.log"
                
            log_message(f"Using standard mode log path: {log_file_path}", "SETUP")
    
    # Create an empty log file if it doesn't exist (though the module will do this too)
    if not log_file_path.exists():
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        log_file_path.touch()
        log_message(f"Created empty log file at {log_file_path}", "SETUP")
    else:
        log_message(f"Log file already exists at {log_file_path}", "SETUP")
    
    return str(log_file_path)


def update_config(log_file_path, itgmania_path=None, banner_image_path=None):
    """
    Update the display_config.toml with the ITGMania log file path.
    
    Args:
        log_file_path (str): The path to the ITGMania log file.
        itgmania_path (Path, optional): The path to the ITGMania installation.
        banner_image_path (Path, optional): The path to the banner image.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Find the config file path
        config_path = ROOT_DIR / "config" / "display_config.toml"
        
        if not config_path.exists():
            log_message(f"Config file {config_path} does not exist.", "SETUP")
            log_message(f"Error: Config file {config_path} not found.", "ERROR")
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
        
        # Add the banner image path if provided
        if banner_image_path:
            banner_path_str = str(banner_image_path).replace('\\', '/')
            config["dynamic_marquee"]["itgmania_banner_path"] = banner_path_str
            log_message(f"Added ITGMania banner path: {banner_path_str}", "SETUP")
        
        # Add the ITGMania base path if provided
        if itgmania_path:
            # Convert backslashes to forward slashes for TOML-friendliness
            itgmania_path_str = str(itgmania_path).replace('\\', '/')
            config["dynamic_marquee"]["itgmania_base_path"] = itgmania_path_str
            log_message(f"Added ITGMania base path: {itgmania_path_str}", "SETUP")
        
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
        
        log_message(f"Updated display_config.toml with log file path and banner path", "SETUP")
        return True
    
    except Exception as e:
        log_message(f"Error updating config: {str(e)}", "SETUP")
        log_message(f"Error: Failed to update config: {str(e)}", "ERROR")
        return False


def setup_itgmania_integration(itgmania_path, banner_image_path=None):
    """
    Main function to set up ITGMania integration, designed to be called directly from other modules.
    
    Args:
        itgmania_path (str): Path to the ITGMania installation.
        banner_image_path (str, optional): Path to a custom banner image.
        
    Returns:
        bool: True if setup was successful, False otherwise.
    """
    try:
        log_message("==================================================", "SETUP")
        log_message("   Arcade Station - ITGMania Integration Setup", "SETUP")
        log_message("==================================================", "SETUP")
        
        # Convert string paths to Path objects
        itgmania_path = Path(itgmania_path)
        if banner_image_path:
            banner_image_path = Path(banner_image_path)
        
        # Validate the ITGMania path and get the corrected base path
        is_valid, base_path = validate_itgmania_path(itgmania_path)
        if not is_valid:
            log_message("Proceeding despite validation issues.", "SETUP")
        
        # Use the corrected base path from validation
        itgmania_path = base_path
        
        log_message(f"Using ITGMania installation at: {itgmania_path}", "SETUP")
        
        # Copy module files
        log_message("Step 1: Copying module file to ITGMania installation...", "SETUP")
        success, (dest_file, dest_image, is_portable) = copy_shim_files(itgmania_path)
        if not success:
            return False
        
        # Determine log file path
        log_message("Step 2: Determining log file path...", "SETUP")
        log_file_path = determine_log_file_path(itgmania_path, dest_file, is_portable)
        
        # Update config
        log_message("Step 3: Updating configuration...", "SETUP")
        
        # Use the provided banner image if specified, otherwise use the copied one
        banner_path = banner_image_path if banner_image_path else dest_image
        
        if not update_config(log_file_path, itgmania_path, banner_path):
            return False
        
        log_message("==================================================", "SETUP")
        log_message("   Setup Complete!", "SETUP")
        log_message("==================================================", "SETUP")
        log_message("ITGMania is now configured to work with Arcade Station's dynamic marquee.", "SETUP")
        log_message(f"Log file path: {log_file_path}", "SETUP")
        if banner_path:
            log_message(f"Banner image path: {banner_path}", "SETUP")
        
        return True
        
    except Exception as e:
        log_message(f"Setup failed: {str(e)}", "ERROR")
        
        # Print traceback for debugging
        import traceback
        traceback.print_exc()
        
        return False


def main():
    """
    Command-line entry point when script is run directly.
    Prompts the user for the ITGMania installation path and sets up the integration.
    """
    try:
        # Interactive mode
        print("Running ITGMania integration setup in interactive mode.")
        
        # Get ITGMania path from user input
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
        
        # Run the setup function
        if setup_itgmania_integration(itgmania_path):
            print("\nSetup completed successfully!")
            print("To use this feature:")
            print("1. Make sure Arcade Station is running")
            print("2. Launch ITGMania")
            print("3. Select songs to see their banners on your marquee display")
        else:
            print("\nSetup failed. Check the error messages above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nSetup canceled by user.")
        sys.exit(1)


if __name__ == "__main__":
    main() 