import keyboard
import subprocess
import tomllib
import os
import platform

def get_os():
    """
    Returns the current operating system.
    """
    return platform.system()

def start_app(executable_path):
    """
    Function to start an application given its executable path.
    """
    try:
        os_type = get_os()
        print(f"Starting process [{executable_path}] on {os_type}...")
        if os_type == "Windows":
            subprocess.Popen(f'start {executable_path}', shell=True)
        elif os_type == "Darwin":
            subprocess.Popen(['open', executable_path])
        else:
            subprocess.Popen(['xdg-open', executable_path])
        print(f"Launched process [{executable_path}].")
    except Exception as e:
        print(f"Failed to start process: {e}")

def load_key_mappings(config_path):
    """
    Load key-action mappings from a TOML configuration file.
    """
    with open(config_path, 'rb') as file:
        config = tomllib.load(file)
    return config.get('key_mappings', {})

def main():
    # Load key mappings from the TOML file
    config_path = os.path.join(os.path.dirname(__file__), '../../../config/key_listener.toml')
    key_mappings = load_key_mappings(config_path)

    # Register hotkeys based on the mappings
    for hotkey, action in key_mappings.items():
        keyboard.add_hotkey(hotkey, lambda action=action: start_app(action))

    print("Listener started. Press Ctrl+C to stop.")
    try:
        # Block forever, waiting for hotkeys
        keyboard.wait()
    except KeyboardInterrupt:
        print("Listener stopped.")

if __name__ == "__main__":
    main() 