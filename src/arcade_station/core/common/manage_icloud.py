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
import tempfile

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
        
        # Format process array for PowerShell
        processes_array = ','.join([f'"{p}"' for p in processes_to_restart])
        
        # Create a wrapper batch file to launch PowerShell with all parameters in hidden mode
        # The "/b" parameter with "start" runs the command without creating a window
        bat_content = f"""@echo off
start /b powershell.exe -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden ^
    -File "{ps_script_path}" ^
    -AppleServicesPath "{apple_services_path}" ^
    -ProcessesToRestart {processes_array} ^
    -UploadDirectory "{upload_directory}" ^
    -IntervalSeconds {interval_seconds} ^
    -DeleteAfterUpload ${str(delete_after_upload).lower()}
"""
        
        # Save the batch file to a temporary location
        fd, batch_path = tempfile.mkstemp(suffix='.bat')
        with os.fdopen(fd, 'w') as f:
            f.write(bat_content)
        
        log_message(f"Created temporary batch file at: {batch_path}", "ICLOUD")
        log_message(f"Batch file contents:\n{bat_content}", "ICLOUD")
        
        # Configure for completely hidden execution
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE - completely hidden
        
        # Launch the process with no window
        process = subprocess.Popen(
            batch_path,
            creationflags=subprocess.CREATE_NO_WINDOW,  # No window instead of new console
            startupinfo=startupinfo,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        log_message(f"iCloud upload management started with PID: {process.pid}", "ICLOUD")
        return process
        
    except Exception as e:
        log_message(f"Failed to start iCloud upload management: {e}", "ICLOUD")
        return None

def create_standalone_script(visible=True):
    """
    Creates a standalone batch script that can be manually executed for testing.
    This is useful for troubleshooting when the automated launching doesn't work.
    
    Args:
        visible (bool): Whether the script should show a console window when run
    
    Returns:
        str: Path to the created batch file
    """
    try:
        # Load configuration
        config = load_toml_config('screenshot_config.toml')
        icloud_config = config.get('icloud_upload', {})
        
        # Get parameters
        apple_services_path = icloud_config.get('apple_services_path', '')
        processes_to_restart = icloud_config.get('processes_to_restart', [])
        upload_directory = icloud_config.get('upload_directory', '')
        interval_seconds = icloud_config.get('interval_seconds', 300)
        delete_after_upload = icloud_config.get('delete_after_upload', True)
        
        # Path to PowerShell script
        ps_script_path = os.path.join(
            base_dir, '..', 'windows', 'manage_icloud_uploads.ps1'
        )
        ps_script_path = os.path.normpath(ps_script_path)
        
        # Format process array for PowerShell
        processes_array = ','.join([f'"{p}"' for p in processes_to_restart])
        
        # Create batch file content - visible or hidden version
        if visible:
            # Visible version for debugging
            bat_content = f"""@echo off
echo Starting iCloud Upload Management...
echo.
powershell.exe -ExecutionPolicy Bypass -NoProfile ^
    -File "{ps_script_path}" ^
    -AppleServicesPath "{apple_services_path}" ^
    -ProcessesToRestart {processes_array} ^
    -UploadDirectory "{upload_directory}" ^
    -IntervalSeconds {interval_seconds} ^
    -DeleteAfterUpload ${str(delete_after_upload).lower()}

pause
"""
            filename = "run_icloud_uploader_visible.bat"
        else:
            # Hidden version for production
            bat_content = f"""@echo off
start /b powershell.exe -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden ^
    -File "{ps_script_path}" ^
    -AppleServicesPath "{apple_services_path}" ^
    -ProcessesToRestart {processes_array} ^
    -UploadDirectory "{upload_directory}" ^
    -IntervalSeconds {interval_seconds} ^
    -DeleteAfterUpload ${str(delete_after_upload).lower()}
"""
            filename = "run_icloud_uploader_hidden.bat"
        
        # Save to a named file in the current directory
        output_path = os.path.join(os.getcwd(), filename)
        with open(output_path, 'w') as f:
            f.write(bat_content)
            
        log_message(f"Created standalone batch file at: {output_path}", "ICLOUD")
        return output_path
        
    except Exception as e:
        log_message(f"Failed to create standalone script: {e}", "ICLOUD")
        return None

if __name__ == "__main__":
    # When run directly, create both visible and hidden standalone scripts
    visible_script = create_standalone_script(visible=True)
    hidden_script = create_standalone_script(visible=False)
    
    if visible_script and hidden_script:
        print(f"Created visible script for testing: {visible_script}")
        print(f"Created hidden script for production: {hidden_script}")
    
    print("Starting iCloud upload management service in background...")
    process = manage_icloud_uploads()
    if process:
        print(f"Service started invisibly with PID: {process.pid}")
    else:
        print("Failed to start service. Check logs for details.") 