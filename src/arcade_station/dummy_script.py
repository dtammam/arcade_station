import sys
import os
# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from arcade_station.core.common.core_functions import *

def main():
    """
    Main function to demonstrate the use of open_header from core_functions.
    """
    # Call the open_header function with the current script file name
    open_header(os.path.basename(__file__))

if __name__ == "__main__":
    main()