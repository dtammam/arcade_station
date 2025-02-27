"""
Monitor ITGMania song selection log file and update the marquee display.

This script watches a specified file for changes. When the file is updated,
it reads the file to find a banner line, extracts the image path, and 
updates the marquee display using the display_image function.
"""

import os
import sys
import time
import re
from pathlib import Path

# Add the parent directory of 'arcade_station' to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from arcade_station.core.common.core_functions import (
    load_toml_config, 
    log_message,
    kill_process_by_identifier
)
from arcade_station.core.common.display_image import display_image


def monitor_itgmania_log(config_path='display_config.toml'):
    """
    Monitor the ITGMania log file for changes and update the marquee display.
    
    Args:
        config_path (str): Path to the display configuration file.
    """
    # Load configuration
    try:
        config = load_toml_config(config_path)
        dynamic_marquee_config = config.get('dynamic_marquee', {})
        display_config = config.get('display', {})
        
        # Check if ITGMania display is enabled
        if not dynamic_marquee_config.get('itgmania_display_enabled', False):
            log_message("ITGMania display is disabled in configuration", "BANNER")
            return
        
        # Get the log file path
        log_file_path = dynamic_marquee_config.get('itgmania_display_file_path')
        fallback_banner_path = display_config.get('default_image_path')
        
        if not log_file_path:
            log_message("ITGMania log file path not specified in configuration", "BANNER")
            return
        
        # Verify log file directory exists and resolve any user variables in path
        log_file_path = os.path.expanduser(log_file_path)
        log_file_path = os.path.normpath(log_file_path)
        log_file = Path(log_file_path)
        
        log_message(f"Using resolved ITGMania log file path: {log_file}", "BANNER")
        
        if not log_file.parent.exists():
            log_message(f"Directory for ITGMania log file does not exist: {log_file.parent}", "BANNER")
            log_message(f"Will attempt to create directory: {log_file.parent}", "BANNER")
            try:
                log_file.parent.mkdir(parents=True, exist_ok=True)
                log_message(f"Created directory: {log_file.parent}", "BANNER")
            except Exception as e:
                log_message(f"Failed to create directory: {str(e)}", "BANNER")
                return
        
        # Create the file if it doesn't exist
        if not log_file.exists():
            log_file.touch()
            log_message(f"Created ITGMania log file: {log_file}", "BANNER")
        
        # Get initial modification time
        last_mod_time = log_file.stat().st_mtime
        
        log_message(f"Monitoring ITGMania log file: {log_file}", "BANNER")
        log_message(f"Using fallback banner: {fallback_banner_path}", "BANNER")
        
        # Main monitoring loop
        while True:
            try:
                # Check if the file exists
                if log_file.exists():
                    # Get current modification time
                    current_mod_time = log_file.stat().st_mtime
                    
                    # If the file has been modified
                    if current_mod_time > last_mod_time:
                        log_message(f"ITGMania log file updated: {log_file}", "BANNER")
                        update_marquee_from_file(str(log_file), fallback_banner_path, display_config)
                        
                        # Small delay to ensure the file is not being written to
                        time.sleep(1)
                        
                        # Update last modification time
                        last_mod_time = current_mod_time
                else:
                    log_message(f"ITGMania log file no longer exists: {log_file}", "BANNER")
                    log_message("Attempting to recreate the file", "BANNER")
                    try:
                        log_file.touch()
                        log_message(f"Recreated ITGMania log file: {log_file}", "BANNER")
                        last_mod_time = log_file.stat().st_mtime
                    except Exception as e:
                        log_message(f"Failed to recreate log file: {str(e)}", "BANNER")
            except Exception as e:
                log_message(f"Error monitoring ITGMania log file: {str(e)}", "BANNER")
            
            # Sleep to prevent high CPU usage
            time.sleep(1)
            
    except Exception as e:
        log_message(f"Failed to monitor ITGMania log file: {str(e)}", "BANNER")


def update_marquee_from_file(file_path, fallback_banner_path, display_config):
    """
    Parse the ITGMania log file and update the marquee with the banner image.
    
    Args:
        file_path (str): Path to the ITGMania log file.
        fallback_banner_path (str): Path to the fallback banner image.
        display_config (dict): Display configuration.
    """
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Kill any existing marquee image process before displaying a new one
        log_message("Killing any existing marquee image processes", "BANNER")
        kill_process_by_identifier("marquee_image")
        
        # Extract the banner path using regex
        banner_match = re.search(r'Banner: (.+)$', content, re.MULTILINE)
        
        if banner_match:
            banner_path = banner_match.group(1).strip()
            log_message(f"Found banner path in log file: {banner_path}", "BANNER")
            
            # Check if the banner file exists
            if os.path.exists(banner_path):
                # Update the display with the banner image
                background_color = display_config.get('background_color', 'black')
                display_image(banner_path, background_color)
                log_message(f"Updated marquee display with banner: {banner_path}", "BANNER")
            else:
                log_message(f"Banner file does not exist: {banner_path}", "BANNER")
                if fallback_banner_path and os.path.exists(fallback_banner_path):
                    display_image(fallback_banner_path, display_config.get('background_color', 'black'))
                    log_message(f"Using fallback banner: {fallback_banner_path}", "BANNER")
        else:
            log_message("No banner path found in log file", "BANNER")
            if fallback_banner_path and os.path.exists(fallback_banner_path):
                display_image(fallback_banner_path, display_config.get('background_color', 'black'))
                log_message(f"Using fallback banner: {fallback_banner_path}", "BANNER")
    except Exception as e:
        log_message(f"Error updating marquee from file: {str(e)}", "BANNER")
        if fallback_banner_path and os.path.exists(fallback_banner_path):
            display_image(fallback_banner_path, display_config.get('background_color', 'black'))
            log_message(f"Using fallback banner due to error: {fallback_banner_path}", "BANNER")


if __name__ == "__main__":
    monitor_itgmania_log() 