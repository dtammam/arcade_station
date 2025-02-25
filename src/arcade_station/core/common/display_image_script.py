import sys
import os
import argparse
import logging

# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

from arcade_station.core.common.display_image import run_image_display

def main():
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    
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
            logging.error(f"Image file not found: {args.image_path}")
            sys.exit(1)
            
        logging.debug(f"Starting image display - Image: {args.image_path}, Color: {args.background_color}, Monitor: {args.monitor_index}")
        
        # Run the image display function
        run_image_display(args.image_path, args.background_color, args.monitor_index)
    
    except Exception as e:
        logging.error(f"Error in image display script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
