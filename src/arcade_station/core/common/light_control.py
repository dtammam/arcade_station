import subprocess
import platform
from arcade_station.core.common.core_functions import load_toml_config

def reset_lights():
    """
    Resets the lights using the LightsTest.exe if configured.
    """
    config = load_toml_config('utility_config.toml')
    lights_config = config.get('lights', {})
    executable_path = lights_config.get('light_reset_executable_path')
    enabled = lights_config.get('lights_enabled', False)

    if enabled and executable_path and platform.system() == 'Windows':
        try:
            print("Starting light test...")
            process = subprocess.Popen(executable_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.communicate(timeout=0.325)
            process.terminate()
            print("Stopped light test.")
        except Exception as e:
            print(f"Failed to reset lights: {e}")

def launch_mame_lights():
    """
    Launches mame2lit.exe if lights are enabled and the game is MAME-based.
    """
    config = load_toml_config('utility_config.toml')
    lights_config = config.get('lights', {})
    mame_executable_path = lights_config.get('light_mame_executable_path')
    enabled = lights_config.get('lights_enabled', False)

    if enabled and mame_executable_path and platform.system() == 'Windows':
        try:
            print("Launching MAME lights...")
            subprocess.Popen(mame_executable_path, shell=True)
            print("MAME lights launched.")
        except Exception as e:
            print(f"Failed to launch MAME lights: {e}")
