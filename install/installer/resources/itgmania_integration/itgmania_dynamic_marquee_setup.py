"""
Setup ITGMania Dynamic Marquee Integration

This script sets up the integration between Arcade Station and ITGMania by:
1. Finding the correct ITGMania installation base directory
2. Copying module files to the ITGMania installation
3. Determining the proper log file path
4. Configuring the display_config.toml with the correct paths

The script handles both portable and standard installations, as well as situations
where users provide paths to executables instead of the base directory.
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


def copy_shim_files(itgmania_path, custom_banner_path=None):
    """
    Copy the module file to the appropriate ITGMania location.
    
    Checks if ITGMania is running in portable mode (has Portable.ini) and installs
    to the appropriate location - either the install directory or AppData.
    
    Args:
        itgmania_path (Path): The path to the ITGMania installation.
        custom_banner_path (Path, optional): Path to a custom banner image to use.
    
    Returns:
        bool: True if successful, False otherwise.
        tuple: (dest_file, dest_image, is_portable) - Destination file paths and portable mode status
    """
    try:
        # Source paths for the module files
        source_lua = SCRIPT_DIR / "ArcadeStationMarquee.lua"
        source_png = SCRIPT_DIR / "itgmania.png"
        
        # Use custom banner if provided
        has_custom_banner = False
        if custom_banner_path and os.path.exists(custom_banner_path):
            source_png = Path(custom_banner_path)
            has_custom_banner = True
            log_message(f"Using custom banner image: {source_png}", "SETUP")
        
        if not source_lua.exists():
            log_message(f"Module file {source_lua} does not exist.", "SETUP")
            log_message(f"Error: Module file {source_lua} not found.", "ERROR")
            return False, (None, None, False)
            
        if not has_custom_banner and not source_png.exists():
            log_message(f"Fallback image {source_png} does not exist.", "SETUP")
            log_message(f"Warning: Fallback image {source_png} not found. Will use default theme image.", "WARNING")
        
        # Ensure itgmania_path is a Path object
        if not isinstance(itgmania_path, Path):
            itgmania_path = Path(itgmania_path)
        
        # Verify that itgmania_path looks correct
        if not itgmania_path.exists():
            log_message(f"ITGMania path {itgmania_path} does not exist.", "SETUP")
            log_message(f"Error: ITGMania path {itgmania_path} not found.", "ERROR")
            return False, (None, None, False)
        
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
            # If using a custom banner, keep its original filename
            if has_custom_banner:
                dest_png = dest_dir / source_png.name
            else:
                dest_png = dest_dir / "itgmania.png"
            
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
    log_message(f"Determining log file path for ITGMania at: {itgmania_path}", "SETUP")
    
    # Ensure we're working with a Path object
    itgmania_path = Path(itgmania_path)
    
    # Make sure we're using the base directory, not an executable
    if itgmania_path.is_file():
        log_message(f"Warning: Log path determination was given an executable: {itgmania_path}", "SETUP")
        itgmania_path = itgmania_path.parent
        # If in a Program directory, go up one level
        if itgmania_path.name.lower() == "program":
            itgmania_path = itgmania_path.parent
            log_message(f"Adjusted to parent directory: {itgmania_path}", "SETUP")
    
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
    
    # Double-check that the log file's parent directory is not an executable
    # This is a safeguard against paths like "C:/ITGMania/Program/ITGmania.exe/Themes/..."
    log_path_parts = list(log_file_path.parts)
    new_log_path_parts = []
    executable_found = False
    
    for part in log_path_parts:
        if part.lower().endswith(('.exe', '.app')):
            log_message(f"Warning: Log path contains executable part: {part}", "SETUP")
            executable_found = True
            # Skip this part
            continue
        new_log_path_parts.append(part)
    
    if executable_found:
        log_file_path = Path(*new_log_path_parts)
        log_message(f"Corrected log path: {log_file_path}", "SETUP")
    
    # Create an empty log file if it doesn't exist (though the module will do this too)
    try:
        if not log_file_path.exists():
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            log_file_path.touch()
            log_message(f"Created empty log file at {log_file_path}", "SETUP")
        else:
            log_message(f"Log file already exists at {log_file_path}", "SETUP")
    except Exception as e:
        log_message(f"Warning: Could not create log file: {e}", "SETUP")
    
    return str(log_file_path)


def update_config(config_path: str, log_file_path: str, banner_path: str) -> bool:
    """Update display_config.toml with ITGMania log file and banner paths.
    
    Args:
        config_path: Path to display_config.toml
        log_file_path: Path to ITGMania log file
        banner_path: Path to banner image
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not os.path.exists(config_path):
            log_message(f"Config file not found at {config_path}", "SETUP")
            return False
            
        # Ensure the log file path uses forward slashes for TOML
        log_file_path = log_file_path.replace('\\', '/')
        log_message(f"Using normalized log file path: {log_file_path}", "SETUP")
        
        # Read current config
        with open(config_path, "rb") as f:
            try:
                config = tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                log_message(f"Error decoding TOML: {e}", "SETUP")
                return False
        
        # Ensure dynamic_marquee section exists
        if "dynamic_marquee" not in config:
            config["dynamic_marquee"] = {}
        
        # Update settings - explicitly set each field to ensure they're all updated
        config["dynamic_marquee"]["enabled"] = True
        config["dynamic_marquee"]["itgmania_display_enabled"] = True
        config["dynamic_marquee"]["itgmania_display_file_path"] = log_file_path
        
        # Set banner path if provided
        if banner_path:
            banner_path = banner_path.replace('\\', '/')
            config["dynamic_marquee"]["itgmania_banner_path"] = banner_path
            log_message(f"Setting banner path: {banner_path}", "SETUP")
        
        # Write updated config
        with open(config_path, "w") as f:
            # Since tomllib doesn't support writing, we'll manually write the file
            for section, values in config.items():
                f.write(f"[{section}]\n")
                for key, value in values.items():
                    if isinstance(value, bool):
                        f.write(f"{key} = {str(value).lower()}\n")
                    elif isinstance(value, (int, float)):
                        f.write(f"{key} = {value}\n")
                    elif isinstance(value, str):
                        f.write(f'{key} = "{value}"\n')
                    else:
                        f.write(f"{key} = {value}\n")
                f.write("\n")
        
        # Verify the file was written correctly
        if os.path.exists(config_path):
            log_message(f"Config updated successfully at {config_path}", "SETUP")
            
            # Verify the log path was set correctly
            with open(config_path, "rb") as f:
                try:
                    updated_config = tomllib.load(f)
                    if "dynamic_marquee" in updated_config and "itgmania_display_file_path" in updated_config["dynamic_marquee"]:
                        actual_path = updated_config["dynamic_marquee"]["itgmania_display_file_path"]
                        log_message(f"Verified log path in config: {actual_path}", "SETUP")
                        if actual_path != log_file_path:
                            log_message(f"Log path mismatch! Expected: {log_file_path}, Got: {actual_path}", "SETUP")
                    else:
                        log_message("Could not find itgmania_display_file_path in updated config", "SETUP")
                except Exception as e:
                    log_message(f"Error verifying config update: {e}", "SETUP")
            
            return True
        else:
            log_message(f"Config file not found after writing: {config_path}", "SETUP")
            return False
    except Exception as e:
        log_message(f"Error updating config: {e}", "SETUP")
        return False


def find_correct_itgmania_path(input_path):
    """
    Directly find the correct ITGMania base path by checking for the Themes directory.
    This is a more direct approach than trying to parse paths.
    
    Args:
        input_path (str or Path): The user-provided path to ITGMania
        
    Returns:
        Path: The corrected ITGMania base path
    """
    # Convert to Path object if it's a string
    if isinstance(input_path, str):
        input_path = Path(input_path)
    
    log_message(f"Finding correct ITGMania path from: {input_path}", "SETUP")
    
    # If it's a file (executable), start with its parent directory
    if input_path.is_file():
        log_message(f"Input is a file, starting with parent directory", "SETUP")
        current_dir = input_path.parent
    else:
        current_dir = input_path
    
    # Check the current directory for Themes
    if (current_dir / "Themes").exists():
        log_message(f"Found Themes in current directory: {current_dir}", "SETUP")
        return current_dir
    
    # Check if we're in a Program directory and the parent has Themes
    if current_dir.name.lower() == "program":
        parent_dir = current_dir.parent
        if (parent_dir / "Themes").exists():
            log_message(f"Found Themes in parent directory: {parent_dir}", "SETUP")
            return parent_dir
    
    # Check parent directory
    parent_dir = current_dir.parent
    if (parent_dir / "Themes").exists():
        log_message(f"Found Themes in parent directory: {parent_dir}", "SETUP")
        return parent_dir
    
    # Search subdirectories for Themes (limited depth)
    for root, dirs, files in os.walk(current_dir):
        if "Themes" in dirs:
            themes_dir = Path(root) / "Themes"
            if themes_dir.exists():
                log_message(f"Found Themes directory in subdirectory: {Path(root)}", "SETUP")
                return Path(root)
    
    # If we still haven't found it, look for the structure in common locations
    common_locations = [
        Path("C:/Games/ITGmania"),
        Path("C:/ITGmania"),
        Path(os.path.expanduser("~/ITGmania")),
        Path("D:/Games/ITGmania"),
        Path("/Applications/ITGmania")
    ]
    
    for location in common_locations:
        if location.exists() and (location / "Themes").exists():
            log_message(f"Found ITGMania in common location: {location}", "SETUP")
            return location
    
    # If all else fails, return the original directory but log a warning
    log_message(f"Could not find Themes directory, using original path: {current_dir}", "SETUP")
    return current_dir


def get_correct_log_file_path(itgmania_base_path, is_portable=False):
    """
    Determine the correct log file path based on a validated ITGMania base path.
    
    Args:
        itgmania_base_path (Path): The validated ITGMania base path
        is_portable (bool): Whether ITGMania is running in portable mode
    
    Returns:
        str: The correct log file path
    """
    log_message(f"Determining log file path from base: {itgmania_base_path}", "SETUP")
    
    # The correct log path should always be in the Modules directory under Themes/Simply Love
    if is_portable:
        # For portable mode, use the installation directory
        log_path = itgmania_base_path / "Themes" / "Simply Love" / "Modules" / "ArcadeStationMarquee.log"
        log_message(f"Using portable log path: {log_path}", "SETUP")
    else:
        # For standard mode, use the AppData location
        system = platform.system().lower()
        if system == "windows":
            appdata_dir = Path(os.path.expandvars("%APPDATA%")) / "ITGmania"
        elif system == "darwin":
            appdata_dir = Path.home() / "Library" / "Preferences" / "ITGmania"
        elif system == "linux":
            appdata_dir = Path.home() / ".itgmania"
        else:
            appdata_dir = itgmania_base_path / "AppData"
        
        log_path = appdata_dir / "Themes" / "Simply Love" / "Modules" / "ArcadeStationMarquee.log"
        log_message(f"Using standard mode log path: {log_path}", "SETUP")
    
    # Ensure the directory exists
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Return a properly formatted path string
    return str(log_path).replace("\\", "/")


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
        
        # Find the correct ITGMania base path directly
        log_message(f"Input ITGMania path: {itgmania_path}", "SETUP")
        itgmania_base_path = find_correct_itgmania_path(itgmania_path)
        log_message(f"Using ITGMania base path: {itgmania_base_path}", "SETUP")
        
        if banner_image_path:
            banner_image_path = Path(banner_image_path)
            log_message(f"Using custom banner image: {banner_image_path}", "SETUP")
        
        # Check for portable mode
        is_portable = (itgmania_base_path / "Portable.ini").exists()
        if is_portable:
            log_message("Detected portable mode installation", "SETUP")
        else:
            log_message("Detected standard installation (using AppData)", "SETUP")
        
        # Copy module files
        log_message("Step 1: Copying module file to ITGMania installation...", "SETUP")
        success, (dest_file, dest_image, _) = copy_shim_files(itgmania_base_path, banner_image_path)
        if not success:
            return False
        
        # Determine log file path directly
        log_message("Step 2: Determining log file path...", "SETUP")
        log_file_path = get_correct_log_file_path(itgmania_base_path, is_portable)
        log_message(f"Final log file path: {log_file_path}", "SETUP")
        
        # Update config
        log_message("Step 3: Updating configuration...", "SETUP")
        
        # Use the provided banner image if specified, otherwise use the copied one
        banner_path = banner_image_path if banner_image_path else dest_image
        
        if not update_config(ROOT_DIR / "config" / "display_config.toml", log_file_path, str(banner_path)):
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