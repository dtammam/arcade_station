"""
Start Streaming Module

This module handles launching OBS and optional webcam management software
for streaming purposes across different platforms (Windows, Linux, macOS).
"""

import os
import platform
import subprocess
import sys
import time
from pathlib import Path

# Add the parent directory to the Python path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from arcade_station.core.common.core_functions import (
    load_toml_config,
    log_message
)


def start_streaming():
    """
    Launch OBS and optionally webcam management software based on configuration.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get configuration from TOML file
        config = load_toml_config("utility_config.toml")
        streaming_config = config.get("streaming", {})
        
        # Get executable paths and settings
        obs_executable = streaming_config.get("obs_executable", "")
        webcam_executable = streaming_config.get("webcam_management_executable", "")
        launch_webcam = streaming_config.get("webcam_management_enabled", False)
        obs_arguments = streaming_config.get("obs_arguments", "")
        
        # Validate OBS executable path
        if not obs_executable:
            log_message("Error: OBS executable path is not configured in utility_config.toml", "STREAMING")
            return False
            
        if not os.path.exists(obs_executable):
            log_message(f"Error: OBS executable not found at {obs_executable}", "STREAMING")
            return False
        
        # Launch webcam management software if configured
        if launch_webcam and webcam_executable and os.path.exists(webcam_executable):
            log_message(f"Launching webcam management software: {webcam_executable}", "STREAMING")
            
            # Handle platform-specific process creation
            try:
                current_os = platform.system().lower()
                if current_os == "windows":
                    # Use CREATE_NO_WINDOW flag (0x08000000) on Windows
                    subprocess.Popen(
                        [webcam_executable],
                        creationflags=0x08000000,
                        shell=False
                    )
                else:
                    # Linux/Mac approach
                    subprocess.Popen(
                        [webcam_executable],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        start_new_session=True
                    )
                log_message("Webcam management software launched successfully", "STREAMING")
                
                # Give webcam software a moment to initialize
                time.sleep(2)
                
            except Exception as e:
                log_message(f"Warning: Failed to launch webcam management software: {str(e)}", "STREAMING")
        
        # Launch OBS
        log_message(f"Launching OBS: {obs_executable}", "STREAMING")
        
        # Parse arguments if provided
        args = [obs_executable]
        if obs_arguments:
            args.extend(obs_arguments.split())
        
        # Handle platform-specific process creation
        current_os = platform.system().lower()
        if current_os == "windows":
            # Get the directory containing the executable
            obs_dir = os.path.dirname(obs_executable)
            os.chdir(obs_dir)  # Change to OBS directory for proper operation
            
            # Start OBS with arguments
            subprocess.Popen(
                args,
                creationflags=0x08000000,  # CREATE_NO_WINDOW flag
                shell=False
            )
        else:
            # Linux/Mac approach
            subprocess.Popen(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
        
        log_message("OBS launched successfully", "STREAMING")
        return True
        
    except Exception as e:
        log_message(f"Error starting streaming: {str(e)}", "STREAMING")
        return False


if __name__ == "__main__":
    # When run directly, execute the streaming function
    success = start_streaming()
    sys.exit(0 if success else 1)