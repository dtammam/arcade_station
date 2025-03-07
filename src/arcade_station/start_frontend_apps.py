"""
Arcade Station Frontend Launcher.

This is the main entry point for starting the Arcade Station application.
It handles initialization of the environment, launches required background
services, sets up the frontend, and manages the overall application lifecycle.

The module performs the following key tasks:
1. Verifies Python version compatibility
2. Sets up the virtual environment if needed
3. Prepares the system by killing conflicting processes
4. Launches background services (key listeners, OSD, etc.)
5. Starts the Pegasus frontend
6. Displays the default marquee/banner image

This script should be run directly to start the Arcade Station system.
"""

import sys
import os
import time
import argparse
import traceback

# Check Python version
REQUIRED_VERSION = (3, 12, 9)  # Updated to 3.12.9
version_info = sys.version_info[:3]
current_version = f"{version_info[0]}.{version_info[1]}.{version_info[2]}"
required_version_str = ".".join(map(str, REQUIRED_VERSION))

if version_info != REQUIRED_VERSION:
    print(f"Warning: This application was developed with Python {required_version_str}")
    print(f"Current version: {current_version}")
    print("Some features may not work correctly.")

# Add the project root to the Python path
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base_dir, '..'))

from arcade_station.core.common.core_functions import (
    launch_script, 
    log_message, 
    load_toml_config,
    kill_processes_from_toml,
    determine_operating_system
)
from arcade_station.core.common.display_image import display_image_from_config
from arcade_station.core.common.launch_binary import launch_osd

def setup_virtual_environment():
    """
    Set up and activate the Python virtual environment for Arcade Station.
    
    Checks if the script is already running in a virtual environment. If not,
    it attempts to locate and activate the project's virtual environment.
    This ensures all dependencies are available and isolated from the system
    Python installation.
    
    Returns:
        bool: True if already in a virtual environment or if activation was
              successful, False if the virtual environment couldn't be found
              or activated.
    """
    try:
        # Check if we're already in a virtual environment
        if sys.prefix != sys.base_prefix:
            log_message("Already running in a virtual environment.", "STARTUP")
            return True
        
        # Get the project root directory
        project_root = os.path.abspath(os.path.join(base_dir, '..', '..'))
        venv_path = os.path.join(project_root, ".venv")
        
        # Check if venv exists
        if not os.path.exists(venv_path):
            log_message(f"Virtual environment not found at {venv_path}", "STARTUP")
            return False
        
        # Activate the virtual environment by modifying environment variables
        os_type = determine_operating_system()
        if os_type == "Windows":
            activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
            if not os.path.exists(activate_script):
                log_message(f"Activation script not found at {activate_script}", "STARTUP")
                return False
            
            # Set environment variables for activation
            os.environ["PATH"] = os.path.join(venv_path, "Scripts") + os.pathsep + os.environ["PATH"]
            os.environ["VIRTUAL_ENV"] = venv_path
        else:  # Linux/Mac
            activate_script = os.path.join(venv_path, "bin", "activate")
            if not os.path.exists(activate_script):
                log_message(f"Activation script not found at {activate_script}", "STARTUP")
                return False
            
            # Set environment variables for activation
            os.environ["PATH"] = os.path.join(venv_path, "bin") + os.pathsep + os.environ["PATH"]
            os.environ["VIRTUAL_ENV"] = venv_path
        
        # Remove PYTHONHOME if it exists as it can interfere with virtual environments
        if "PYTHONHOME" in os.environ:
            del os.environ["PYTHONHOME"]
        
        log_message(f"Virtual environment activated at {venv_path}", "STARTUP")
        return True
    
    except Exception as e:
        log_message(f"Failed to setup virtual environment: {e}", "STARTUP")
        return False

def prepare_system():
    """
    Prepare the system environment for Arcade Station startup.
    
    Terminates any existing processes that might conflict with Arcade Station,
    such as previous instances of the frontend, game processes, or utilities.
    This ensures a clean state before launching the application components.
    
    Returns:
        bool: True if system preparation was successful, False otherwise.
    """
    try:
        log_message("Preparing system by killing processes and resetting state...", "STARTUP")
        
        # Kill any existing processes that might interfere
        kill_processes_from_toml('processes_to_kill.toml')
        
        # Optional: Wait a moment to ensure processes are killed
        time.sleep(1)
        
        log_message("System preparation complete", "STARTUP")
        return True
    except Exception as e:
        log_message(f"Failed to prepare system: {e}", "STARTUP")
        return False

def start_conditional_scripts():
    """
    Launch optional background services based on configuration settings.
    
    Reads the utility_config.toml and display_config.toml files to determine
    which optional services should be started. This includes:
    - VPN connection service (if enabled)
    - On-screen display (OSD) service (Windows-only, if enabled)
    - Dynamic marquee monitors for specific games (if enabled)
    - ITGMania song banner display (if enabled)
    
    Returns:
        None
    
    Note:
        Some services are platform-specific and will only be launched on
        compatible operating systems.
    """
    try:
        # Load configuration
        utility_config = load_toml_config('utility_config.toml')
        vpn_enabled = utility_config.get('vpn', {}).get('enabled', False)
        if vpn_enabled:
            vpn_script = os.path.join(base_dir, "core", "common", "connect_vpn.py")
            vpn_process = launch_script(vpn_script, identifier="connect_vpn")
            log_message(f"Launched VPN connection script with PID: {vpn_process.pid}", "STARTUP")
        
        # OSD configuration - Launch OSD if enabled (Windows-only)
        osd_enabled = utility_config.get('osd', {}).get('enabled', False)
        if osd_enabled and determine_operating_system() == "Windows":
            if launch_osd():
                log_message("Successfully launched OSD application", "STARTUP")
            else:
                log_message("Failed to launch OSD application", "STARTUP")
        
        # Dynamic marquee configuration - Launch ITGMania monitor
        display_config = load_toml_config('display_config.toml')
        dynamic_marquee_enabled = display_config.get('dynamic_marquee', {}).get('enabled', False)
        itgmania_display_enabled = display_config.get('dynamic_marquee', {}).get('itgmania_display_enabled', False)
        
        if dynamic_marquee_enabled and itgmania_display_enabled:
            itgmania_script = os.path.join(base_dir, "launchers", "monitor_itgmania.py")
            itgmania_process = launch_script(itgmania_script, identifier="monitor_itgmania")
            log_message(f"Launched ITGMania monitor script with PID: {itgmania_process.pid}", "STARTUP")
        
        # iCloud upload management configuration (Windows-only)
        screenshot_config = load_toml_config('screenshot_config.toml')
        icloud_enabled = screenshot_config.get('icloud_upload', {}).get('enabled', False)
        
        if icloud_enabled and determine_operating_system() == "Windows":
            log_message("iCloud upload enabled and running on Windows - starting upload manager", "STARTUP")
            
            try:
                # Launch the iCloud manager as a separate process
                icloud_script = os.path.join(base_dir, "core", "common", "manage_icloud.py")
                icloud_process = launch_script(icloud_script, identifier="manage_icloud")
                log_message(f"Launched iCloud manager with PID: {icloud_process.pid}", "STARTUP")
            except Exception as e:
                log_message(f"Error starting iCloud manager: {e}", "STARTUP")
                log_message(traceback.format_exc(), "STARTUP")
        
        # Other conditional scripts can be added here based on configuration
        
    except Exception as e:
        log_message(f"Error starting conditional scripts: {e}", "STARTUP")

def main():
    """
    Main entry point for the Arcade Station application.
    
    This function orchestrates the startup sequence for Arcade Station:
    1. Parses command-line arguments
    2. Sets up the virtual environment
    3. Prepares the system by killing conflicting processes
    4. Displays the default marquee/banner image
    5. Launches the keyboard shortcut listener
    6. Starts conditional background services based on configuration
    7. Launches the Pegasus frontend
    8. If in shell replacement mode, keeps the process running
    
    Command-line Arguments:
        --shell-mode: Run in shell replacement mode, keeping the process alive
                     to prevent the shell from returning to the command prompt.
    
    Returns:
        None
    """
    parser = argparse.ArgumentParser(description='Start Arcade Station frontend applications')
    parser.add_argument('--shell-mode', action='store_true', help='Run in shell replacement mode')
    args = parser.parse_args()
    
    log_message("Starting Arcade Station frontend applications...", "STARTUP")
    
    # Setup virtual environment if needed
    venv_setup = setup_virtual_environment()
    if not venv_setup:
        log_message("Warning: Virtual environment setup failed, continuing with system Python", "STARTUP")
    
    # Prepare the system state
    system_ready = prepare_system()
    if not system_ready:
        log_message("Warning: System preparation failed, continuing anyway", "STARTUP")
    
    # Display default image using the standardized approach
    default_image_process = display_image_from_config(use_default=True)
    log_message(f"Launched default image display with standardized process", "BANNER")
    
    # Launch the key_listener.py script with the appropriate identifier
    listener_script = os.path.join(base_dir, "listeners", "key_listener.py")
    listener_process = launch_script(listener_script, identifier="key_listener")
    log_message(f"Launched key_listener.py with PID: {listener_process.pid}", "MENU")
    
    # Start conditional scripts based on configuration
    start_conditional_scripts()
    
    # Use kill_all_and_reset_pegasus.py to launch Pegasus (replaced the direct Pegasus launch)
    reset_script = os.path.join(base_dir, "core", "common", "kill_all_and_reset_pegasus.py")
    reset_process = launch_script(reset_script, identifier="kill_all_and_reset_pegasus")
    log_message(f"Launched kill_all_and_reset_pegasus.py with PID: {reset_process.pid}", "RESET")
    
    # If running in shell replacement mode, we need to keep this process running
    if args.shell_mode:
        log_message("Running in shell replacement mode, keeping process alive", "STARTUP")
        try:
            # Keep the main process running until interrupted
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            log_message("Received keyboard interrupt, shutting down", "STARTUP")
    else:
        log_message("All frontend applications started successfully", "STARTUP")

if __name__ == "__main__":
    main()