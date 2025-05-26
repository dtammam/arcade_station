"""
Debug Pegasus Launch Issues.

This script helps diagnose and fix issues with launching Pegasus after installation.
It performs a series of checks and attempts different methods to launch Pegasus.

Run this script after installation if Pegasus doesn't start normally.
"""

import sys
import os
import time
import subprocess
import platform
import argparse

# Add the root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from arcade_station.core.common.core_functions import (
    log_message,
    load_toml_config,
    kill_processes_from_toml,
    kill_process_by_identifier,
    determine_operating_system
)

def scan_for_pegasus_binary():
    """Recursively scan for Pegasus binary in common locations."""
    log_message("Scanning for Pegasus binary...", "DEBUG")
    
    # Define binary names for different OS
    binary_names = {
        "Windows": ["pegasus-fe_windows.exe"],
        "Darwin": ["pegasus-fe_mac"],
        "Linux": ["pegasus-fe_linux"]
    }
    
    # Get the current OS binary names
    os_type = determine_operating_system()
    names_to_search = binary_names.get(os_type, [])
    if not names_to_search:
        log_message(f"Unknown OS type: {os_type}, using all known binary names", "DEBUG")
        names_to_search = [name for sublist in binary_names.values() for name in sublist]
    
    log_message(f"Looking for: {names_to_search}", "DEBUG")
    
    # Define search locations
    locations_to_search = [
        os.path.dirname(sys.executable),  # Python executable directory
        os.path.join(os.path.dirname(sys.executable), ".."),  # Parent of Python executable directory
        os.path.dirname(os.path.abspath(__file__)),  # Script directory
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."),  # Parent of script directory
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."),  # Two levels up from script
        os.path.abspath(".")  # Current working directory
    ]
    
    # Add pegasus-fe subdirectory to each location
    extended_locations = []
    for location in locations_to_search:
        extended_locations.append(location)
        extended_locations.append(os.path.join(location, "pegasus-fe"))
    
    log_message(f"Searching in {len(extended_locations)} locations", "DEBUG")
    
    # Search for binaries
    found_binaries = []
    for location in extended_locations:
        if not os.path.exists(location):
            continue
            
        log_message(f"Scanning: {location}", "DEBUG")
        
        # Direct check in this directory
        for binary_name in names_to_search:
            binary_path = os.path.join(location, binary_name)
            if os.path.exists(binary_path):
                log_message(f"Found: {binary_path}", "DEBUG")
                found_binaries.append(binary_path)
        
        # Recursive check (limited depth)
        for root, dirs, files in os.walk(location):
            # Control recursion depth
            relative_path = os.path.relpath(root, location)
            if relative_path.count(os.sep) > 2:  # Limit depth to 2 levels
                continue
                
            for binary_name in names_to_search:
                if binary_name in files:
                    binary_path = os.path.join(root, binary_name)
                    log_message(f"Found: {binary_path}", "DEBUG")
                    found_binaries.append(binary_path)
    
    return found_binaries

def try_launch_pegasus(binary_path):
    """Attempt to launch Pegasus using the specified binary path."""
    log_message(f"Attempting to launch: {binary_path}", "DEBUG")
    
    # Check if file exists and is executable
    if not os.path.exists(binary_path):
        log_message(f"Binary does not exist: {binary_path}", "DEBUG")
        return False
    
    if not os.access(binary_path, os.X_OK) and platform.system() != "Windows":
        log_message(f"Binary is not executable: {binary_path}", "DEBUG")
        try:
            os.chmod(binary_path, 0o755)  # Make executable
            log_message("Made binary executable", "DEBUG")
        except Exception as e:
            log_message(f"Failed to make binary executable: {e}", "DEBUG")
            return False
    
    try:
        # Get the directory containing the binary to use as working directory
        working_dir = os.path.dirname(binary_path)
        
        # Launch with platform-specific approach
        if platform.system() == "Windows":
            # Windows
            log_message("Using Windows launch method", "DEBUG")
            process = subprocess.Popen(
                binary_path,
                shell=True,
                cwd=working_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # macOS and Linux
            log_message("Using Unix launch method", "DEBUG")
            process = subprocess.Popen(
                [binary_path],
                cwd=working_dir
            )
        
        # Wait a moment to see if process stays running
        time.sleep(2)
        
        if process.poll() is None:
            log_message("Process is still running - launch successful!", "DEBUG")
            return True
        else:
            log_message(f"Process exited immediately with code: {process.returncode}", "DEBUG")
            return False
            
    except Exception as e:
        log_message(f"Error launching process: {e}", "DEBUG")
        import traceback
        log_message(traceback.format_exc(), "DEBUG")
        return False

def repair_pegasus_configuration():
    """Attempt to repair Pegasus configuration by updating config files with correct paths."""
    log_message("Attempting to repair Pegasus configuration...", "DEBUG")
    
    try:
        # Find Pegasus binaries
        binaries = scan_for_pegasus_binary()
        if not binaries:
            log_message("No Pegasus binaries found, cannot repair configuration", "DEBUG")
            return False
        
        # Choose the first binary found
        binary_path = binaries[0]
        log_message(f"Using binary for repair: {binary_path}", "DEBUG")
        
        # Get the binary name and directory
        binary_name = os.path.basename(binary_path)
        binary_dir = os.path.dirname(binary_path)
        
        # Load configuration
        try:
            installed_games = load_toml_config('pegasus_binaries.toml')
            
            # Update the configuration
            os_type = determine_operating_system()
            updated_config = False
            
            if os_type == "Windows" and binary_name.endswith(".exe"):
                if 'pegasus' in installed_games and 'windows_binary' in installed_games['pegasus']:
                    if installed_games['pegasus']['windows_binary'] != binary_name:
                        log_message(f"Updating Windows binary name to: {binary_name}", "DEBUG")
                        # We cannot modify the TOML directly since we can't write to it
                        # Instead, print instructions for manual update
                        updated_config = True
            elif os_type == "Darwin":
                if 'pegasus' in installed_games and 'mac_binary' in installed_games['pegasus']:
                    if installed_games['pegasus']['mac_binary'] != binary_name:
                        log_message(f"Mac binary name should be updated to: {binary_name}", "DEBUG")
                        updated_config = True
            elif os_type == "Linux":
                if 'pegasus' in installed_games and 'linux_binary' in installed_games['pegasus']:
                    if installed_games['pegasus']['linux_binary'] != binary_name:
                        log_message(f"Linux binary name should be updated to: {binary_name}", "DEBUG")
                        updated_config = True
            
            if updated_config:
                log_message("Configuration update required. Please update manually:", "DEBUG")
                log_message(f"Edit pegasus_binaries.toml and ensure the binary name matches: {binary_name}", "DEBUG")
                log_message(f"The pegasus-fe directory should be: {binary_dir}", "DEBUG")
            else:
                log_message("Configuration seems correct, no updates needed", "DEBUG")
            
            return True
                
        except Exception as e:
            log_message(f"Error loading or updating configuration: {e}", "DEBUG")
            import traceback
            log_message(traceback.format_exc(), "DEBUG")
            return False
            
    except Exception as e:
        log_message(f"Error in repair attempt: {e}", "DEBUG")
        import traceback
        log_message(traceback.format_exc(), "DEBUG")
        return False

def generate_pegasus_launch_script(binary_path):
    """Generate a direct launch script for Pegasus that bypasses the normal startup flow."""
    log_message(f"Generating direct launch script for: {binary_path}", "DEBUG")
    
    # Determine script extension based on OS
    os_type = determine_operating_system()
    if os_type == "Windows":
        script_name = "launch_pegasus_direct.bat"
        script_content = f"""@echo off
echo Direct Pegasus Launcher
echo ---------------------
cd "{os.path.dirname(binary_path)}"
start "" "{binary_path}"
"""
    else:
        script_name = "launch_pegasus_direct.sh"
        script_content = f"""#!/bin/bash
echo "Direct Pegasus Launcher"
echo "---------------------"
cd "{os.path.dirname(binary_path)}"
"{binary_path}"
"""
    
    # Write the script
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
    try:
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make executable on Unix
        if os_type != "Windows":
            os.chmod(script_path, 0o755)
        
        log_message(f"Created direct launcher script: {script_path}", "DEBUG")
        return script_path
    except Exception as e:
        log_message(f"Failed to create launcher script: {e}", "DEBUG")
        return None

def main():
    """Main function to run the diagnostic tool."""
    parser = argparse.ArgumentParser(description='Debug Pegasus launch issues')
    parser.add_argument('--scan-only', action='store_true', help='Only scan for Pegasus binaries without trying to launch')
    parser.add_argument('--repair', action='store_true', help='Attempt to repair Pegasus configuration')
    parser.add_argument('--create-launcher', action='store_true', help='Create a direct launcher script for Pegasus')
    args = parser.parse_args()
    
    log_message("Starting Pegasus launch diagnostics...", "DEBUG")
    log_message(f"Python executable: {sys.executable}", "DEBUG")
    log_message(f"Operating System: {determine_operating_system()}", "DEBUG")
    log_message(f"Current working directory: {os.getcwd()}", "DEBUG")
    log_message(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}", "DEBUG")
    
    # Terminate any existing Pegasus processes
    log_message("Killing any existing Pegasus processes...", "DEBUG")
    kill_processes_from_toml('processes_to_kill.toml')
    
    # Scan for Pegasus binaries
    binaries = scan_for_pegasus_binary()
    
    if not binaries:
        log_message("No Pegasus binaries found!", "DEBUG")
        log_message("Please check your installation. The pegasus-fe directory may be missing or in an unexpected location.", "DEBUG")
        return
    
    log_message(f"Found {len(binaries)} potential Pegasus binaries:", "DEBUG")
    for idx, binary in enumerate(binaries):
        log_message(f"{idx+1}. {binary}", "DEBUG")
    
    # Repair configuration if requested
    if args.repair:
        log_message("Attempting to repair configuration...", "DEBUG")
        repair_pegasus_configuration()
    
    # Create launcher script if requested
    if args.create_launcher:
        log_message("Creating direct launcher script...", "DEBUG")
        launcher_path = generate_pegasus_launch_script(binaries[0])
        if launcher_path:
            log_message(f"Created launcher at: {launcher_path}", "DEBUG")
            log_message(f"You can use this script to launch Pegasus directly.", "DEBUG")
    
    # Skip launch attempt if scan-only
    if args.scan_only:
        log_message("Scan complete. Not attempting to launch (--scan-only specified).", "DEBUG")
        return
    
    # Try to launch each binary
    launch_success = False
    for binary in binaries:
        log_message(f"Attempting to launch: {binary}", "DEBUG")
        if try_launch_pegasus(binary):
            log_message(f"Successfully launched Pegasus from: {binary}", "DEBUG")
            launch_success = True
            break
        else:
            log_message(f"Failed to launch Pegasus from: {binary}", "DEBUG")
    
    if launch_success:
        log_message("Pegasus launched successfully!", "DEBUG")
    else:
        log_message("Failed to launch Pegasus from any of the detected binaries.", "DEBUG")
        log_message("Please check the logs for error details and consider repairing your installation.", "DEBUG")

if __name__ == "__main__":
    main() 