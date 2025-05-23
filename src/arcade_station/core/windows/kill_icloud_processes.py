"""
Windows iCloud Process Management Module.

This module provides functionality for managing iCloud processes on Windows systems,
specifically for the Arcade Station application. It handles:
- Termination of iCloud-related processes (iCloudServices, iCloudPhotos, iCloudDrive)
- Cleanup of Python iCloud manager processes
- Restart of iCloud services with proper sequencing
- Configuration-based process management

The module reads process lists and paths from screenshot_config.toml and provides
both automated and interactive modes of operation.
"""

import os
import sys
import subprocess
import time

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.abspath(os.path.join(script_dir, '..', '..'))
project_root = os.path.abspath(os.path.join(base_dir, '..'))
sys.path.insert(0, project_root)

from arcade_station.core.common.core_functions import (
    log_message,
    load_toml_config
)

def kill_icloud_processes():
    """Kill all running iCloud-related processes."""
    log_message("Stopping iCloud processes...", "ICLOUD_KILL")
    
    # Load config to get the list of processes to kill
    config = load_toml_config('screenshot_config.toml')
    processes_to_restart = config.get('icloud_upload', {}).get('processes_to_restart', 
                                    ["iCloudServices", "iCloudPhotos"])
    
    # Add .exe extension to each process name
    icloud_processes = [f"{process}.exe" for process in processes_to_restart]
    icloud_processes.append("iCloudDrive.exe")  # Add any additional processes
    
    # Kill iCloud processes
    for process in icloud_processes:
        try:
            log_message(f"Attempting to stop {process}...", "ICLOUD_KILL")
            subprocess.run(['taskkill', '/F', '/IM', process], 
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            log_message(f"Stopped {process}", "ICLOUD_KILL")
        except Exception as e:
            log_message(f"Error stopping {process}: {e}", "ICLOUD_KILL")
    
    # Find and kill the Python iCloud manager processes
    try:
        # List all Python processes
        result = subprocess.run(
            ['wmic', 'process', 'where', 'name="python.exe"', 'get', 'processid,commandline'], 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        
        # Parse the output to find processes related to iCloud manager
        for line in result.stdout.splitlines():
            if "manage_icloud.py" in line:
                try:
                    # Extract the PID
                    parts = line.strip().split()
                    if parts:
                        pid = parts[-1]
                        log_message(f"Killing iCloud manager process with PID: {pid}", "ICLOUD_KILL")
                        subprocess.run(['taskkill', '/F', '/PID', pid], 
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except Exception as e:
                    log_message(f"Error parsing process line: {e}", "ICLOUD_KILL")
        
        log_message("All iCloud manager processes have been terminated", "ICLOUD_KILL")
    
    except Exception as e:
        log_message(f"Error killing Python processes: {e}", "ICLOUD_KILL")

def restart_icloud_services():
    """Restart iCloud services using config values."""
    log_message("Restarting iCloud services...", "ICLOUD_KILL")
    
    # Load config to get Apple services path
    config = load_toml_config('screenshot_config.toml')
    icloud_config = config.get('icloud_upload', {})
    
    # Get the Apple services path and processes to restart from config
    apple_path = icloud_config.get('apple_services_path', 
                                  r"C:\Program Files (x86)\Common Files\Apple\Internet Services")
    services = icloud_config.get('processes_to_restart', 
                               ["iCloudServices", "iCloudPhotos"])
    
    # Check if the path exists
    if not os.path.exists(apple_path):
        log_message(f"Apple services path not found: {apple_path}", "ICLOUD_KILL")
        return False
    
    # Stop existing services
    for service in services:
        try:
            log_message(f"Stopping {service}...", "ICLOUD_KILL")
            subprocess.run(['taskkill', '/F', '/IM', f"{service}.exe"], 
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            log_message(f"Error stopping {service}: {e}", "ICLOUD_KILL")
    
    # Wait a moment
    log_message("Waiting for services to stop completely...", "ICLOUD_KILL")
    time.sleep(2)
    
    # Start services
    for service in services:
        try:
            service_path = os.path.join(apple_path, f"{service}.exe")
            if os.path.exists(service_path):
                log_message(f"Starting {service}...", "ICLOUD_KILL")
                subprocess.Popen([service_path])
                log_message(f"Started {service}", "ICLOUD_KILL")
            else:
                log_message(f"Service executable not found: {service_path}", "ICLOUD_KILL")
        except Exception as e:
            log_message(f"Error starting {service}: {e}", "ICLOUD_KILL")
    
    return True

if __name__ == "__main__":
    """
    Main entry point for the iCloud process management script.
    
    When run directly, this script will:
    1. Kill all iCloud-related processes
    2. Prompt the user to restart services
    3. Restart services if requested
    4. Wait for user input before exiting
    """
    # Kill the processes
    kill_icloud_processes()
    
    # Ask if user wants to restart services
    user_input = input("\nDo you want to restart iCloud services? (y/n): ").lower()
    if user_input.startswith('y'):
        restart_icloud_services()
    
    log_message("Operation complete.", "ICLOUD_KILL")
    input("\nPress Enter to exit.") 