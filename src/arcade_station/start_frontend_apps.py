import sys
import os
import platform
import subprocess
import time
import argparse
import json

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
# Commenting out as we'll implement the functionality directly
# from arcade_station.core.common.manage_icloud import manage_icloud_uploads

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

def launch_icloud_manager():
    """
    Launches the iCloud upload management script directly.
    
    Returns:
        subprocess.Popen: The process object for the PowerShell script or None on failure
    """
    try:
        if determine_operating_system() != "Windows":
            log_message("iCloud upload management is only supported on Windows", "ICLOUD")
            return None
        
        # Load configuration
        screenshot_config = load_toml_config('screenshot_config.toml')
        icloud_config = screenshot_config.get('icloud_upload', {})
        
        if not icloud_config.get('enabled', False):
            log_message("iCloud upload management is disabled in configuration", "ICLOUD")
            return None
        
        # Get parameters
        apple_services_path = icloud_config.get('apple_services_path')
        processes_to_restart = icloud_config.get('processes_to_restart', [])
        upload_directory = icloud_config.get('upload_directory')
        interval_seconds = icloud_config.get('interval_seconds', 300)
        delete_after_upload = icloud_config.get('delete_after_upload', True)
        
        # Validate parameters
        if not apple_services_path or not upload_directory or not processes_to_restart:
            log_message("Missing required iCloud configuration parameters", "ICLOUD")
            return None
        
        # Build process array string for PowerShell
        processes_str = ','.join([f'"{p}"' for p in processes_to_restart])
        
        # Path to PowerShell script
        ps_script_path = os.path.join(
            base_dir, "core", "windows", "manage_icloud_uploads.ps1"
        )
        ps_script_path = os.path.normpath(ps_script_path)
        
        if not os.path.exists(ps_script_path):
            log_message(f"PowerShell script not found at {ps_script_path}", "ICLOUD")
            return None
        
        # Debug output for troubleshooting
        log_message("Starting iCloud upload management with parameters:", "ICLOUD")
        log_message(f"- Script path: {ps_script_path}", "ICLOUD")
        log_message(f"- AppleServicesPath: {apple_services_path}", "ICLOUD")
        log_message(f"- ProcessesToRestart: {processes_to_restart}", "ICLOUD")
        log_message(f"- UploadDirectory: {upload_directory}", "ICLOUD")
        log_message(f"- IntervalSeconds: {interval_seconds}", "ICLOUD")
        log_message(f"- DeleteAfterUpload: {delete_after_upload}", "ICLOUD")
        
        # Direct PowerShell command - simplest possible approach
        command = [
            'powershell.exe',
            '-ExecutionPolicy', 'Bypass',
            '-WindowStyle', 'Hidden',
            '-File', ps_script_path,
            '-AppleServicesPath', apple_services_path,
            '-ProcessesToRestart', processes_str,
            '-UploadDirectory', upload_directory,
            '-IntervalSeconds', str(interval_seconds),
            '-DeleteAfterUpload', "$" + str(delete_after_upload).lower()
        ]
        
        log_message(f"Full command: {' '.join(command)}", "ICLOUD")
        
        # Launch PowerShell directly
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,  # Capture output for logging
            stderr=subprocess.PIPE,  # Capture errors for logging
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # Start a thread to read and log output
        def log_output():
            try:
                stdout, stderr = process.communicate(timeout=5)  # Short timeout to avoid blocking
                if stdout:
                    log_message(f"PowerShell output: {stdout.decode('utf-8', errors='ignore')}", "ICLOUD")
                if stderr:
                    log_message(f"PowerShell error: {stderr.decode('utf-8', errors='ignore')}", "ICLOUD")
            except subprocess.TimeoutExpired:
                # Process is still running, which is expected for long-running scripts
                log_message("PowerShell script is running in background", "ICLOUD")
                pass
        
        # Start output logging in a separate thread to avoid blocking
        import threading
        threading.Thread(target=log_output, daemon=True).start()
        
        log_message(f"iCloud upload management started with PID: {process.pid}", "ICLOUD")
        return process
    
    except Exception as e:
        log_message(f"Failed to start iCloud upload management: {str(e)}", "ICLOUD")
        import traceback
        log_message(f"Stack trace: {traceback.format_exc()}", "ICLOUD")
        return None

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
        
        # OSD configuration - Launch OSD if enabled (Windows-only)
        osd_enabled = utility_config.get('osd', {}).get('enabled', False)
        if osd_enabled and determine_operating_system() == "Windows":
            if launch_osd():
                log_message("Successfully launched OSD application", "STARTUP")
            else:
                log_message("Failed to launch OSD application", "STARTUP")
        
        # Dynamic marquee configuration
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
            # Direct approach instead of using manage_icloud.py module
            icloud_process = launch_icloud_manager()
            if icloud_process:
                log_message(f"Launched iCloud upload management with PID: {icloud_process.pid}", "STARTUP")
            else:
                log_message("Failed to launch iCloud upload management", "STARTUP")
        
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