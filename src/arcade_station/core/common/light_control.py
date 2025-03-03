import subprocess
import platform
import psutil
import time
import os
from arcade_station.core.common.core_functions import load_toml_config, launch_script, log_message

def kill_lights_processes():
    """
    Kill all running LightsTest and mame2lit processes to ensure COM port is released.
    Uses multiple methods to ensure processes are properly terminated.
    """
    light_processes = ["LightsTest", "mame2lit", "LightsTest.exe", "mame2lit.exe"]
    killed_any = False
    
    # First method: Use psutil to find and kill by process name
    for proc in psutil.process_iter(['name', 'exe']):
        try:
            proc_name = proc.info['name']
            proc_exe = proc.info.get('exe', '')
            
            # Check both process name and executable path
            if any(light_proc.lower() in proc_name.lower() for light_proc in light_processes) or \
               any(light_proc.lower() in proc_exe.lower() for light_proc in light_processes):
                log_message(f"Killing lights process: {proc_name} (PID: {proc.pid})", "LIGHTS")
                try:
                    proc.kill()
                    proc.wait(timeout=1)
                    killed_any = True
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    log_message(f"Error killing process {proc_name}: {e}", "LIGHTS")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            continue
    
    # Second method: Use taskkill on Windows for stubborn processes
    if platform.system() == 'Windows':
        for proc_name in light_processes:
            try:
                # Force kill with taskkill
                log_message(f"Force killing {proc_name} with taskkill", "LIGHTS")
                subprocess.run(['taskkill', '/F', '/IM', proc_name], 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)
                killed_any = True
            except Exception as e:
                # Ignore errors as the process might not exist
                pass
    
    # Allow a brief pause if we killed anything
    if killed_any:
        log_message("Waiting for lights processes to fully terminate...", "LIGHTS")
        time.sleep(0.5)
    
    return killed_any

def reset_lights():
    """
    Resets the lights using the LightsTest.exe if configured.
    Ensures all light processes are properly terminated.
    """
    # Always kill any existing lights processes first
    kill_lights_processes()
    
    config = load_toml_config('utility_config.toml')
    lights_config = config.get('lights', {})
    executable_path = lights_config.get('light_reset_executable_path')
    enabled = lights_config.get('enabled', False)

    if enabled and executable_path and platform.system() == 'Windows':
        try:
            log_message("Starting light test...", "LIGHTS")
            process = subprocess.Popen(executable_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for a short time to let it initialize the lights
            process.communicate(timeout=0.325)
            
            # Terminate the process
            process.terminate()
            
            try:
                # Wait for process to terminate
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate nicely
                process.kill()
                
            log_message("Stopped light test.", "LIGHTS")
            
            # Make absolutely sure no LightsTest processes remain running
            # Critical second check after attempted termination
            time.sleep(0.2)  # Give the system a moment
            kill_lights_processes()
            
        except Exception as e:
            log_message(f"Failed to reset lights: {e}", "LIGHTS")
            # Try to cleanup in case of error
            kill_lights_processes()

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
            # Kill any existing lights processes before launching new ones
            kill_lights_processes()
            
            log_message("Launching MAME lights...", "LIGHTS")
            launch_script(mame_executable_path, identifier="mame_lights")
            log_message("MAME lights launched.", "LIGHTS")
        except Exception as e:
            log_message(f"Failed to launch MAME lights: {e}", "LIGHTS")
