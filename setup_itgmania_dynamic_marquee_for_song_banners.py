"""
ITGMania Dynamic Marquee Integration Setup for Song Banners

This script launches the ITGMania dynamic marquee integration setup process
that allows song banners to be displayed on your marquee display.

The integration uses Simply Love's module system to track song selection and
gameplay events, displaying the appropriate banner on your secondary display.
"""

import os
import sys
import importlib.util
from pathlib import Path

# Get the root directory of the project
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))

# Run the installer script
if __name__ == "__main__":
    try:
        installer_path = script_dir / "installer" / "itgmania_dynamic_marquee" / "setup.py"
        
        if not installer_path.exists():
            print(f"Error: Setup script not found at {installer_path}")
            sys.exit(1)
        
        # Use importlib to load the module
        spec = importlib.util.spec_from_file_location("itgmania_setup", installer_path)
        setup_module = importlib.util.module_from_spec(spec)
        sys.modules["itgmania_setup"] = setup_module
        spec.loader.exec_module(setup_module)
        
        # Run the main function if it exists
        if hasattr(setup_module, "main"):
            setup_module.main()
        
    except Exception as e:
        print(f"Error: {e}")
        
        # Show additional information for debugging
        print("\nTroubleshooting information:")
        print(f"Python executable: {sys.executable}")
        print(f"Script directory: {script_dir}")
        print(f"Python path: {sys.path}")
        
        import traceback
        traceback.print_exc()
        
        sys.exit(1) 