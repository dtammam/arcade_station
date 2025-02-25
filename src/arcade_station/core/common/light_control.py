import subprocess
import platform
from arcade_station.core.common.core_functions import load_toml_config, launch_script, log_message

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
            log_message("Starting light test...", "LIGHTS")
            process = subprocess.Popen(executable_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.communicate(timeout=0.325)
            process.terminate()
            log_message("Stopped light test.", "LIGHTS")
        except Exception as e:
            log_message(f"Failed to reset lights: {e}", "LIGHTS")

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
            log_message("Launching MAME lights...", "LIGHTS")
            launch_script(mame_executable_path, identifier="mame_lights")
            log_message("MAME lights launched.", "LIGHTS")
        except Exception as e:
            log_message(f"Failed to launch MAME lights: {e}", "LIGHTS")
