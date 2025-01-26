import os
from core.core_functions import open_header

def main():
    """
    Main function to demonstrate the use of open_header from core_functions.
    """
    # Call the open_header function with the current script file name
    open_header(os.path.basename(__file__))

if __name__ == "__main__":
    main()