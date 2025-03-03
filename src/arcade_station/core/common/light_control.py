import subprocess
import platform
import psutil
import time
import os
from arcade_station.core.common.core_functions import load_toml_config, launch_script, log_message

def kill_lights_processes():
    """
    Kill all running LightsTest and mame2lit processes to ensure COM port is released.
    """
    light_processes = ["LightsTest", "mame2lit"]
    
    for proc in psutil.process_iter(['name']):
        try:
            proc_name = proc.info['name']
            if any(light_proc in proc_name for light_proc in light_processes):
                log_message(f"Killing lights process: {proc_name}", "LIGHTS")
                proc.kill()
                proc.wait(timeout=1)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            log_message(f"Error killing lights process: {e}", "LIGHTS")

def kill_specific_lights_process(process_name):
    """
    Kill a specific lights-related process by name.
    """
    for proc in psutil.process_iter(['name']):
        try:
            proc_name = proc.info['name']
            if process_name in proc_name:
                log_message(f"Killing specific lights process: {proc_name}", "LIGHTS")
                proc.kill()
                proc.wait(timeout=1)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            log_message(f"Error killing specific lights process: {e}", "LIGHTS")

def reset_lights():
    """
    Resets the lights using the LightsTest.exe if configured.
    """
    # Only kill LightsTest, not mame2lit
    kill_specific_lights_process("LightsTest")
    
    config = load_toml_config('utility_config.toml')
    lights_config = config.get('lights', {})
    executable_path = lights_config.get('light_reset_executable_path')
    enabled = lights_config.get('enabled', False)

    if enabled and executable_path and platform.system() == 'Windows':
        try:
            log_message("Starting light test...", "LIGHTS")
            # Run in a separate process with a short timeout
            process = subprocess.Popen([executable_path], 
                                     creationflags=subprocess.CREATE_NO_WINDOW,
                                     shell=False)
            # Allow it to run briefly
            time.sleep(0.3)
            # Force kill the process
            if process.poll() is None:  # If process is still running
                process.kill()  # Force kill instead of terminate
                log_message("Forcefully killed light test process", "LIGHTS")
            # Ensure it's gone
            kill_specific_lights_process("LightsTest")
            log_message("Light test completed and process confirmed killed", "LIGHTS")
        except Exception as e:
            log_message(f"Failed to reset lights: {e}", "LIGHTS")
            # Still try to kill any remaining processes
            kill_specific_lights_process("LightsTest")

def launch_mame_lights():
    """
    Launches mame2lit.exe if lights are enabled and the game is MAME-based.
    """
    config = load_toml_config('utility_config.toml')
    lights_config = config.get('lights', {})
    mame_executable_path = lights_config.get('light_mame_executable_path')
    enabled = lights_config.get('enabled', False)

    if enabled and mame_executable_path and platform.system() == 'Windows':
        try:
            # Only kill existing mame2lit processes before launching a new one
            kill_specific_lights_process("mame2lit")
            
            log_message("Launching MAME lights...", "LIGHTS")
            
            # Check if the executable path exists
            if not os.path.exists(mame_executable_path):
                log_message(f"MAME lights executable not found at: {mame_executable_path}", "LIGHTS")
                return
            
            # Launch mame2lit.exe directly as an executable, not as a Python script
            process = subprocess.Popen(
                [mame_executable_path],
                creationflags=subprocess.CREATE_NO_WINDOW,
                shell=False
            )
            
            log_message(f"MAME lights launched with PID: {process.pid}", "LIGHTS")
        except Exception as e:
            log_message(f"Failed to launch MAME lights: {e}", "LIGHTS")
