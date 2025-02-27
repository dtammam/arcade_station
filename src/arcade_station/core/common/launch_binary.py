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
import platform

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from arcade_station.core.common.core_functions import start_app, log_message, open_header, load_toml_config, determine_operating_system

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