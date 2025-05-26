"""
Light Control Module for Arcade Station.

This module provides functionality for managing arcade cabinet lighting systems,
including process management for LightsTest and mame2lit applications, and
lighting control operations.
"""

import subprocess
import platform
import psutil
import time
import os
from arcade_station.core.common.core_functions import load_toml_config, launch_script, log_message

def kill_lights_processes():
    """
    Kill all running LightsTest and mame2lit processes.
    
    Terminates any running instances of LightsTest and mame2lit to ensure
    the COM port is released for other applications. This is particularly
    important when switching between different lighting control applications.
    
    Returns:
        None. All operations are logged for debugging purposes.
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
    
    Terminates a single lights-related process identified by its name.
    This is used when only a specific lighting control application needs
    to be stopped, rather than all lighting processes.
    
    Args:
        process_name (str): The name of the process to terminate (e.g., "LightsTest").
    
    Returns:
        None. All operations are logged for debugging purposes.
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
    Reset the arcade cabinet lights to their default state.
    
    Uses LightsTest.exe to reset the lighting system if enabled in the
    configuration. The process is run briefly and then terminated to
    ensure the lights are reset without leaving the process running.
    
    The function:
    1. Terminates any existing LightsTest processes
    2. Checks if lights are enabled in the configuration
    3. Runs LightsTest.exe briefly if enabled
    4. Ensures the process is properly terminated
    
    Returns:
        None. All operations are logged for debugging purposes.
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
    Launch the MAME-specific lighting control application.
    
    Starts mame2lit.exe if lights are enabled in the configuration and
    the system is running Windows. This function is specifically for
    MAME-based games that support lighting control.
    
    The function:
    1. Checks if lights are enabled in the configuration
    2. Terminates any existing mame2lit processes
    3. Launches a new instance of mame2lit.exe
    4. Logs the process ID for tracking
    
    Returns:
        None. All operations are logged for debugging purposes.
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
