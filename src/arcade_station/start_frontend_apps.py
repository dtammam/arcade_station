import sys
import os
import platform
import subprocess
import time
import argparse

# Check Python version
if sys.version_info[:3] != (3, 12, 8):
    print(f"Warning: This application was developed with Python 3.12.8")
    print(f"Current version: {sys.version.split()[0]}")
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

def setup_virtual_environment():
    """
    Sets up and activates the virtual environment if needed.
    Returns True if successful, False otherwise.
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
    Prepares the system by killing any existing processes and resetting the system state.
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
    Start additional scripts based on configuration settings.
    """
    # Load configuration
    try:
        # VPN configuration
        utility_config = load_toml_config('utility_config.toml')
        vpn_enabled = utility_config.get('vpn', {}).get('enabled', False)
        if vpn_enabled:
            vpn_script = os.path.join(base_dir, "core", "common", "connect_vpn.py")
            vpn_process = launch_script(vpn_script, identifier="connect_vpn")
            log_message(f"Launched VPN connection script with PID: {vpn_process.pid}", "STARTUP")
        
        # Dynamic marquee configuration
        display_config = load_toml_config('display_config.toml')
        dynamic_marquee_enabled = display_config.get('dynamic_marquee', {}).get('enabled', False)
        itgmania_display_enabled = display_config.get('dynamic_marquee', {}).get('itgmania_display_enabled', False)
        
        if dynamic_marquee_enabled and itgmania_display_enabled:
            itgmania_script = os.path.join(base_dir, "launchers", "monitor_itgmania.py")
            itgmania_process = launch_script(itgmania_script, identifier="monitor_itgmania")
            log_message(f"Launched ITGMania monitor script with PID: {itgmania_process.pid}", "STARTUP")
        
        # Other conditional scripts can be added here based on configuration
        
    except Exception as e:
        log_message(f"Error starting conditional scripts: {e}", "STARTUP")

def main():
    """
    Main function to start the frontend applications.
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
    
    # Launch the start_pegasus.py script with its identifier
    pegasus_script = os.path.join(base_dir, "core", "common", "start_pegasus.py")
    pegasus_process = launch_script(pegasus_script, identifier="start_pegasus")
    log_message(f"Launched start_pegasus.py with PID: {pegasus_process.pid}", "GAME")
    
    # Start conditional scripts based on configuration
    start_conditional_scripts()
    
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