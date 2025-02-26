import sys
import os
import argparse

# Add the parent directory of 'arcade_station' to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from arcade_station.core.common.core_functions import launch_script

def main():
    parser = argparse.ArgumentParser(
        description="Launch a Python script with a configured virtual environment."
    )
    parser.add_argument("script", help="Path to the Python script to launch.")
    parser.add_argument(
        "--identifier",
        default=None,
        help="Optional identifier to pass to the script (e.g., '--identifier=open_image')."
    )
    args = parser.parse_args()
    script_path = os.path.abspath(args.script)
    if not os.path.exists(script_path):
        print(f"Error: script not found at {script_path}")
        sys.exit(1)
    process = launch_script(script_path, identifier=args.identifier)
    print(f"Launched process with PID: {process.pid}")

if __name__ == "__main__":
    main() 