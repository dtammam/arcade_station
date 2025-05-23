"""
Image Display Script for Arcade Station.

This script provides a command-line interface for displaying images on specific monitors
in the Arcade Station system. It handles argument parsing, file validation, and error
logging for the image display functionality.
"""

import sys
import os
import argparse

# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

from arcade_station.core.common.display_image import run_image_display
from arcade_station.core.common.core_functions import log_message

def main():
    """
    Main entry point for the image display script.
    
    Parses command-line arguments, validates the image file, and initiates
    the image display process on the specified monitor.
    
    Command-line Arguments:
        image_path: Path to the image file to display
        background_color: Background color (e.g., "black", "#000000")
        monitor_index: Index of the monitor to display on
        --identifier: Optional process identifier (default: 'marquee_image')
    
    Returns:
        None. Exits with status code 1 on error.
    """
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description='Display an image on a monitor')
        parser.add_argument('image_path', help='Path to the image file to display')
        parser.add_argument('background_color', help='Background color (e.g., "black", "#000000")')
        parser.add_argument('monitor_index', type=int, help='Index of the monitor to display on')
        parser.add_argument('--identifier', default='marquee_image', help='Process identifier')
        
        args = parser.parse_args()
        
        # Verify image file exists
        if not os.path.exists(args.image_path):
            log_message(f"Image file not found: {args.image_path}", "BANNER")
            sys.exit(1)
            
        log_message(f"Starting image display - Image: {args.image_path}, Color: {args.background_color}, Monitor: {args.monitor_index}", "BANNER")
        
        # Run the image display function
        run_image_display(args.image_path, args.background_color, args.monitor_index)
    
    except Exception as e:
        log_message(f"Error in image display script: {e}", "BANNER")
        sys.exit(1)

if __name__ == "__main__":
    main()
