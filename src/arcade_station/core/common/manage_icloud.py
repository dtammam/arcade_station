"""
Module for managing iCloud photo uploads.

This module reads configuration from screenshot_config.toml and launches
the PowerShell script to manage iCloud services and photo uploads.
"""
import os
import sys
import platform
import subprocess
import logging

# Add the project root to the Python path
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base_dir, '..', '..', '..'))

from arcade_station.core.common.core_functions import (
    load_toml_config,
    log_message,
    determine_operating_system
)

def manage_icloud_uploads():
    """
    Reads the iCloud upload configuration and starts the PowerShell script
    to manage iCloud services and photo uploads.
    
    Returns:
        subprocess.Popen: The process object for the PowerShell script or None on failure
    """
    # Check if we're on Windows
    if determine_operating_system() != "Windows":
        log_message("iCloud upload management is only supported on Windows", "ICLOUD")
        return None
    
    try:
        # Load configuration
        config = load_toml_config('screenshot_config.toml')
        
        # Check if iCloud upload management is enabled
        icloud_config = config.get('icloud_upload', {})
        if not icloud_config.get('enabled', False):
            log_message("iCloud upload management is disabled in configuration", "ICLOUD")
            return None
        
        # Get parameters from config
        apple_services_path = icloud_config.get('apple_services_path')
        processes_to_restart = icloud_config.get('processes_to_restart', [])
        upload_directory = icloud_config.get('upload_directory')
        interval_seconds = icloud_config.get('interval_seconds', 300)
        delete_after_upload = icloud_config.get('delete_after_upload', True)
        
        # Validate required parameters
        if not apple_services_path or not upload_directory or not processes_to_restart:
            log_message("Missing required iCloud configuration parameters", "ICLOUD")
            return None
        
        # Prepare parameters for PowerShell script
        ps_script_path = os.path.join(
            base_dir, '..', 'windows', 'manage_icloud_uploads.ps1'
        )
        ps_script_path = os.path.normpath(ps_script_path)
        
        # Format processes as a PowerShell array string
        processes_str = ','.join([f'"{p}"' for p in processes_to_restart])
        
        # Build PowerShell command
        powershell_exe = "powershell.exe"
        powershell_args = [
            "-ExecutionPolicy", "Bypass",
            "-File", ps_script_path,
            "-AppleServicesPath", f'"{apple_services_path}"',
            "-ProcessesToRestart", f'@({processes_str})',
            "-UploadDirectory", f'"{upload_directory}"',
            "-IntervalSeconds", str(interval_seconds),
            "-DeleteAfterUpload", "$" + ("true" if delete_after_upload else "false")
        ]
        
        # Launch PowerShell script
        cmd = [powershell_exe] + powershell_args
        log_message(f"Starting iCloud upload management script with parameters: {powershell_args}", "ICLOUD")
        
        # Run PowerShell script as a separate process
        process = subprocess.Popen(
            cmd,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        log_message(f"iCloud upload management started with PID: {process.pid}", "ICLOUD")
        return process
        
    except Exception as e:
        log_message(f"Failed to start iCloud upload management: {e}", "ICLOUD")
        return None

if __name__ == "__main__":
    # When run directly, start the iCloud upload management
    manage_icloud_uploads() 