import sys
import os
# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from core.common.display_image import display_image_from_config

if __name__ == "__main__":
    # Enable default mode if "--default" is passed on the command line.
    use_default = "--default" in sys.argv
    display_image_from_config(use_default=use_default)