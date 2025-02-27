"""
Module for managing iCloud photo uploads.

This module reads configuration from screenshot_config.toml and launches
the PowerShell script to manage iCloud services and photo uploads.
"""
import os
import sys
import subprocess
import json

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
        
        # Prepare PowerShell script path
        ps_script_path = os.path.join(base_dir, '..', 'windows', 'manage_icloud_uploads.ps1')
        ps_script_path = os.path.normpath(ps_script_path)
        
        # Create a simple PowerShell command that runs the script as a background job
        # Convert parameters to JSON for safe passing to PowerShell
        params_json = json.dumps({
            'AppleServicesPath': apple_services_path,
            'ProcessesToRestart': processes_to_restart,
            'UploadDirectory': upload_directory,
            'IntervalSeconds': interval_seconds,
            'DeleteAfterUpload': delete_after_upload
        })
        
        # Create the PowerShell command to run our script as a background job
        ps_command = (
            f'Start-Job -ScriptBlock {{ '
            f'$params = ConvertFrom-Json \'{params_json}\'; '
            f'& "{ps_script_path}" '
            f'-AppleServicesPath $params.AppleServicesPath '
            f'-ProcessesToRestart $params.ProcessesToRestart '
            f'-UploadDirectory $params.UploadDirectory '
            f'-IntervalSeconds $params.IntervalSeconds '
            f'-DeleteAfterUpload $params.DeleteAfterUpload '
            f'}}'
        )
        
        # This is the simplest way to launch PowerShell commands invisibly
        process = subprocess.Popen(
            ['powershell.exe', '-WindowStyle', 'Hidden', '-Command', ps_command],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        log_message(f"iCloud upload management started with PID: {process.pid}", "ICLOUD")
        return process
        
    except Exception as e:
        log_message(f"Failed to start iCloud upload management: {e}", "ICLOUD")
        return None

def create_debug_script():
    """
    Creates a simple debug script to test the PowerShell functionality directly.
    
    Returns:
        str: Path to the created PowerShell script
    """
    try:
        # Load configuration
        config = load_toml_config('screenshot_config.toml')
        icloud_config = config.get('icloud_upload', {})
        
        # Path to PowerShell script
        ps_script_path = os.path.join(
            base_dir, '..', 'windows', 'manage_icloud_uploads.ps1'
        )
        ps_script_path = os.path.normpath(ps_script_path)
        
        # Create a simple debug script
        debug_content = f"""
# Test script for iCloud upload management
# Run this directly in PowerShell to debug issues

$AppleServicesPath = "{icloud_config.get('apple_services_path', '')}"
$ProcessesToRestart = @({','.join([f'"{p}"' for p in icloud_config.get('processes_to_restart', [])])})
$UploadDirectory = "{icloud_config.get('upload_directory', '')}"
$IntervalSeconds = {icloud_config.get('interval_seconds', 300)}
$DeleteAfterUpload = ${str(icloud_config.get('delete_after_upload', True)).lower()}

Write-Host "Testing with parameters:"
Write-Host "AppleServicesPath: $AppleServicesPath"
Write-Host "ProcessesToRestart: $ProcessesToRestart"
Write-Host "UploadDirectory: $UploadDirectory"
Write-Host "IntervalSeconds: $IntervalSeconds"
Write-Host "DeleteAfterUpload: $DeleteAfterUpload"
Write-Host ""
Write-Host "Running script..."

& "{ps_script_path}" -AppleServicesPath $AppleServicesPath -ProcessesToRestart $ProcessesToRestart -UploadDirectory $UploadDirectory -IntervalSeconds $IntervalSeconds -DeleteAfterUpload $DeleteAfterUpload
"""
        
        # Save to a debug file
        output_path = os.path.join(os.getcwd(), "debug_icloud_uploader.ps1")
        with open(output_path, 'w') as f:
            f.write(debug_content)
            
        log_message(f"Created debug script at: {output_path}", "ICLOUD")
        return output_path
        
    except Exception as e:
        log_message(f"Failed to create debug script: {e}", "ICLOUD")
        return None

if __name__ == "__main__":
    # When run directly, create debug script and start the service
    debug_script = create_debug_script()
    
    if debug_script:
        print(f"Created debug script at: {debug_script}")
        print("You can run this script directly in PowerShell for testing.")
    
    print("Starting iCloud upload management in background...")
    process = manage_icloud_uploads()
    if process:
        print(f"Service started with PID: {process.pid}")
        print("The service is running invisibly. Check task manager or logs for activity.")
    else:
        print("Failed to start service. Check logs for details.") 