"""
Launch Binary Script

This script can:
1. Launch a binary file passed as a command-line argument
2. Launch specific configured binaries conditionally based on utility_config.toml settings

Usage:
    python launch_binary.py /path/to/binary [--wait]
    python launch_binary.py --type osd
    
Options:
    --wait       Optional flag to wait for the process to complete
    --type TYPE  Launch a predefined binary type (e.g. 'osd', 'vpn')
"""

import os
import sys
import argparse
import psutil
import shutil

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from arcade_station.core.common.core_functions import start_app, log_message, open_header, load_toml_config, determine_operating_system

def prepare_audioswitch_settings():
    """Prepare the AudioSwitch settings directory and copy the Settings.xml file."""
    try:
        # Get the %LOCALAPPDATA% directory
        local_app_data = os.environ.get('LOCALAPPDATA')
        if not local_app_data:
            log_message("LOCALAPPDATA environment variable not found", "OSD")
            return False
        
        # Create the AudioSwitch directory path
        audioswitch_dir = os.path.join(local_app_data, "AudioSwitch")
        
        # Create the directory if it doesn't exist
        if not os.path.exists(audioswitch_dir):
            log_message(f"Creating AudioSwitch directory: {audioswitch_dir}", "OSD")
            os.makedirs(audioswitch_dir)
        
        # Define the source path for the Settings.xml file
        # Look for it in the same directory as the AudioSwitch executable
        config = load_toml_config('utility_config.toml')
        audioswitch_exe_path = config.get('osd', {}).get('sound_osd_executable')
        if not audioswitch_exe_path:
            log_message("AudioSwitch executable path not defined in configuration", "OSD")
            return False
        
        source_dir = os.path.dirname(audioswitch_exe_path)
        settings_xml_source = os.path.join(source_dir, "Settings.xml")
        
        # If Settings.xml doesn't exist in the same directory as the executable,
        # look for it in the bin/windows/AudioSwitch directory
        if not os.path.exists(settings_xml_source):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
            settings_xml_source = os.path.join(base_dir, "bin", "windows", "AudioSwitch", "Settings.xml")
        
        settings_xml_dest = os.path.join(audioswitch_dir, "Settings.xml")
        
        # Check if source Settings.xml exists
        if not os.path.exists(settings_xml_source):
            log_message(f"Settings.xml not found at: {settings_xml_source}", "OSD")
            return False
        
        # Copy the Settings.xml file if it doesn't exist or if it's different
        if not os.path.exists(settings_xml_dest) or not files_are_identical(settings_xml_source, settings_xml_dest):
            log_message(f"Copying Settings.xml to: {settings_xml_dest}", "OSD")
            shutil.copy2(settings_xml_source, settings_xml_dest)
        else:
            log_message("Settings.xml already exists and is up to date", "OSD")
        
        return True
    
    except Exception as e:
        log_message(f"Error preparing AudioSwitch settings: {e}", "OSD")
        return False

def files_are_identical(file1, file2):
    """Compare two files to check if they're identical."""
    try:
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            return f1.read() == f2.read()
    except Exception:
        return False

def launch_osd():
    """Launch the OSD executable if enabled in config and platform is Windows."""
    # Check if running on Windows
    if determine_operating_system() != "Windows":
        log_message("OSD is only supported on Windows.", "OSD")
        return False
    
    # Load configuration
    config = load_toml_config('utility_config.toml')
    
    # Check if OSD is enabled
    if not config.get('osd', {}).get('enabled', False):
        log_message("OSD is disabled in configuration. Skipping launch.", "OSD")
        return False
    
    # Get executable path
    executable_path = config.get('osd', {}).get('sound_osd_executable')
    if not executable_path:
        log_message("OSD executable path not defined in configuration.", "OSD")
        return False
    
    # Check if file exists
    if not os.path.exists(executable_path):
        log_message(f"OSD executable not found at: {executable_path}", "OSD")
        return False
    
    # Prepare AudioSwitch settings before launching
    if not prepare_audioswitch_settings():
        log_message("Warning: Failed to prepare AudioSwitch settings, but continuing with launch", "OSD")
    
    # Launch the application
    log_message(f"Launching OSD application: {executable_path}", "OSD")
    start_app(executable_path)
    return True

def launch_by_type(binary_type):
    """Launch a preconfigured binary based on type."""
    if binary_type.lower() == 'osd':
        return launch_osd()
    else:
        log_message(f"Unknown binary type: {binary_type}", "ERROR")
        return False

def set_process_priority(pid, priority_level="high"):
    """
    Set the priority level of a process.
    
    Args:
        pid (int): Process ID
        priority_level (str): Priority level (low, below_normal, normal, above_normal, high, realtime)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not pid:
            log_message("Cannot set priority - invalid process ID", "GAME")
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
        
        # Set priority
        if priority_level in priority_map:
            process.nice(priority_map[priority_level])
            log_message(f"Set process {pid} priority to {priority_level}", "GAME")
            return True
        else:
            log_message(f"Invalid priority level: {priority_level}", "GAME")
            return False
            
    except Exception as e:
        log_message(f"Failed to set process priority: {e}", "GAME")
        return False

def main():
    """Main function to parse arguments and launch the binary."""
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Launch a binary file.')
    
    # Create mutually exclusive group for binary path or type
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('binary_path', nargs='?', help='Path to the binary file to launch')
    group.add_argument('--type', choices=['osd', 'vpn'], help='Type of preconfigured binary to launch')
    
    # Other arguments
    parser.add_argument('--wait', action='store_true', help='Wait for the process to complete')
    parser.add_argument('--identifier', help='Optional identifier for the process')
    
    args = parser.parse_args()

    # Initialize logging
    open_header("launch_binary")
    
    # Check if we're launching by type or direct path
    if args.type:
        log_message(f"Launching preconfigured binary type: {args.type}", "BINARY")
        success = launch_by_type(args.type)
        if not success:
            log_message(f"Failed to launch {args.type}", "ERROR")
            sys.exit(1)
    else:
        # Get the binary path and validate
        binary_path = args.binary_path
        if not os.path.exists(binary_path):
            log_message(f"Error: Binary not found at path: {binary_path}", "ERROR")
            sys.exit(1)
        
        # Log the launch attempt
        log_message(f"Attempting to launch binary: {binary_path}", "BINARY")
        
        try:
            # Launch the binary using start_app from core_functions
            start_app(binary_path)
            log_message(f"Binary launched successfully: {binary_path}", "BINARY")
            
            # Remove the line that tried to set process priority since we don't have access to the PID here
            # The process creation happens inside start_app and we don't get the PID back
        except Exception as e:
            log_message(f"Failed to launch binary: {e}", "ERROR")
            sys.exit(1)
    
    # If --wait flag is specified, wait for user input before continuing
    if args.wait:
        log_message("Waiting for process to complete...", "BINARY")
        try:
            # Simple pause for demonstration
            input("Press Enter to continue...")
        except KeyboardInterrupt:
            log_message("Process wait interrupted by user", "BINARY")
    
    log_message("Launch binary operation completed", "BINARY")

if __name__ == "__main__":
    main() 