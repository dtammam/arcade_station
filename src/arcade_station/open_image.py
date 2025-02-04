import sys
import os
# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from core.common.display_image import *

if __name__ == "__main__":
    # Display the image based on the configuration in 'display_config.toml'
    display_image_from_config()