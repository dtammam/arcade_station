import keyboard
import subprocess
import os
from arcade_station.core.core_functions import start_app, kill_processes, load_key_mappings

def main():
    # Load key mappings from the TOML file
    config_path = os.path.join(os.path.dirname(__file__), '../../../config/key_listener.toml')
    key_mappings = load_key_mappings(config_path)

    # Register hotkeys based on the mappings
    for hotkey, action in key_mappings.items():
        if action == "kill_processes":
            script_path = os.path.join(os.path.dirname(__file__), '../kill_all_and_reset_pegasus.py')
            keyboard.add_hotkey(hotkey, lambda: subprocess.Popen(['python', script_path]))
        else:
            keyboard.add_hotkey(hotkey, lambda action=action: start_app(action))

    print("Listener started. Press Ctrl+C to stop.")
    try:
        # Block forever, waiting for hotkeys
        keyboard.wait()
    except KeyboardInterrupt:
        print("Listener stopped.")

if __name__ == "__main__":
    main() 