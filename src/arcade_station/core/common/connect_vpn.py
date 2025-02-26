import os
import sys
import time
import subprocess
import psutil

# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

from arcade_station.core.common.core_functions import load_toml_config, log_message

def connect_vpn():
    """
    Connect to VPN directly using Python
    with parameters loaded from utility_config.toml
    """
    # Load VPN configuration from utility_config.toml
    config = load_toml_config('utility_config.toml')
    
    if 'vpn' not in config:
        log_message("VPN configuration not found in utility_config.toml", "VPN")
        return 1
    
    vpn_config = config['vpn']
    
    # Extract VPN parameters
    app_dir = vpn_config.get('vpn_application_directory')
    app_name = vpn_config.get('vpn_application')
    process_name = vpn_config.get('vpn_process')
    config_profile = vpn_config.get('vpn_config_profile')
    seconds_to_wait = vpn_config.get('seconds_to_wait', 10)
    
    # Validate parameters
    if not all([app_dir, app_name, process_name, config_profile]):
        log_message("Missing required VPN parameters in utility_config.toml", "VPN")
        return 1
    
    # Construct full path to VPN application
    vpn_app_path = os.path.join(app_dir, app_name)
    
    # Ensure the VPN application exists
    if not os.path.exists(vpn_app_path):
        log_message(f"VPN application not found at path: {vpn_app_path}", "VPN")
        return 1
    
    log_message(f"Initiating VPN [{app_name}] using config [{config_profile}]...", "VPN")
    
    try:
        # Launch the VPN application with the connect argument
        subprocess.Popen([vpn_app_path, f"--connect \"{config_profile}\""], 
                        shell=True)
        
        log_message(f"Waiting for {seconds_to_wait} seconds before checking VPN process...", "VPN")
        time.sleep(seconds_to_wait)
        
        # Check if the VPN process is running
        vpn_process_running = False
        for proc in psutil.process_iter(['pid', 'name']):
            if process_name.lower() in proc.info['name'].lower():
                vpn_process_running = True
                break
        
        if not vpn_process_running:
            log_message(f"The VPN process [{process_name}] is not running.", "VPN")
            return 1
        
        log_message(f"Validated that the VPN process [{process_name}] is running!", "VPN")
        return 0
        
    except Exception as e:
        log_message(f"Failed to connect to VPN: {e}", "VPN")
        return 1

if __name__ == "__main__":
    sys.exit(connect_vpn()) 