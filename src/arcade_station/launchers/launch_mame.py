import os
import sys
import logging
import subprocess
import platform
import time
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from arcade_station.core.common.core_functions import (
    load_toml_config, 
    log_message,
    convert_path_for_platform,
    run_powershell_script,
    start_process_with_powershell
)

# Platform-specific window focus handling
if platform.system() == "Windows":
    try:
        import win32gui
        import win32process
        import win32con
        import psutil
        has_win32_modules = True
    except ImportError:
        log_message("Windows modules not available for focus management", "MAME")
        has_win32_modules = False
else:
    has_win32_modules = False

def ensure_required_packages():
    """
    Check for and install required packages if they're missing.
    """
    if platform.system() != "Windows":
        return
    
    try:
        import win32gui
        import win32process
        import win32con
        import psutil
        log_message("All required Windows modules available", "MAME")
    except ImportError:
        log_message("Installing required Windows packages for focus management...", "MAME")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32", "psutil"])
            log_message("Successfully installed required packages", "MAME")
            # Need to restart the script to use newly installed packages
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            log_message(f"Failed to install required packages: {str(e)}", "MAME")

def find_mame_window():
    """
    Find the MAME window by looking for windows with 'MAME' or the ROM name in the title.
    Returns the window handle or None if not found.
    """
    if not has_win32_modules:
        return None
        
    result = None
    
    def enum_windows_callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if 'MAME' in window_title:
                results.append(hwnd)
        return True
        
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    
    if windows:
        return windows[0]  # Return first found MAME window
    return None

def refocus_mame(rom_name=None):
    """
    Attempt to find the MAME window and ensure it has focus.
    """
    if not has_win32_modules:
        return False
        
    try:
        # First try by window name
        window_titles = ['MAME']
        if rom_name:
            window_titles.append(rom_name)
        
        for title in window_titles:
            def enum_windows_callback(hwnd, title):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if title.lower() in window_title.lower():
                        return hwnd
                return None
            
            hwnd = None
            windows = []
            win32gui.EnumWindows(lambda h, w: windows.append((h, win32gui.GetWindowText(h))), None)
            
            for h, t in windows:
                if title.lower() in t.lower():
                    hwnd = h
                    break
            
            if hwnd:
                # First make sure the window is not minimized
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                # Set the window as foreground
                win32gui.SetForegroundWindow(hwnd)
                log_message(f"Refocused MAME window by title: {title}", "MAME")
                return True
        
        # If we didn't find by window title, try the more general approach
        hwnd = find_mame_window()
        if hwnd:
            # First make sure the window is not minimized
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            # Set the window as foreground
            win32gui.SetForegroundWindow(hwnd)
            log_message("Refocused MAME window by general search", "MAME")
            return True
        else:
            log_message("MAME window not found for refocusing", "MAME")
            return False
    except Exception as e:
        log_message(f"Failed to refocus MAME window: {str(e)}", "MAME")
        return False

def launch_mame(rom, save_state=None, config_path="display_config.toml"):
    """
    Launch a MAME game with the specified ROM and save state.
    
    Args:
        rom (str): The ROM name to launch.
        save_state (str, optional): The save state to load. Defaults to None.
        config_path (str, optional): Path to the configuration file. Defaults to "display_config.toml".
    """
    # Ensure required packages
    ensure_required_packages()
    
    try:
        # Load configuration
        config = load_toml_config(config_path)
        mame_config = config.get('emulators', {}).get('mame', {})
        
        if not mame_config:
            log_message("MAME configuration not found in config file", "MAME")
            return False
        
        # Get the MAME path and executable
        mame_path = convert_path_for_platform(mame_config.get('path', ''))
        mame_executable = mame_config.get('executable', 'mame.exe')
        mame_ini_path = mame_config.get('ini_path', '-inipath .\ini')
        
        if not mame_path or not os.path.exists(mame_path):
            log_message(f"MAME path not found: {mame_path}", "MAME")
            return False
        
        if not os.path.exists(os.path.join(mame_path, mame_executable)):
            log_message(f"MAME executable not found: {os.path.join(mame_path, mame_executable)}", "MAME")
            return False
        
        # Prepare the save state parameter
        state_param = save_state if save_state else ""
        
        log_message(f"Launching MAME with ROM: {rom}, State: {state_param}", "MAME")
        
        # Platform-specific launch
        if platform.system() == "Windows":
            # Get the current directory to return to it later
            current_dir = os.getcwd()
            
            try:
                # On Windows, prefer to use the PowerShell script
                ps_script_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), 
                    "..", "core", "windows", "StartMAME.ps1"
                )
                
                # Ensure the script exists
                if not os.path.exists(ps_script_path):
                    log_message(f"MAME launch script not found: {ps_script_path}", "MAME")
                    
                    # If script doesn't exist, fall back to using direct PowerShell process starting
                    mame_full_path = os.path.join(mame_path, mame_executable)
                    mame_args = f"{rom} {mame_ini_path}"
                    if state_param:
                        mame_args += f" -state {state_param}"
                    
                    success = start_process_with_powershell(
                        file_path=mame_full_path,
                        working_dir=mame_path,
                        arguments=mame_args
                    )
                    
                    if not success:
                        log_message("Failed to start MAME using PowerShell", "MAME")
                        return False
                else:
                    # Execute the PowerShell script if it exists
                    process = run_powershell_script(
                        script_path=ps_script_path,
                        params={
                            "ROM": rom,
                            "State": state_param,
                            "ExecutablePath": mame_path,
                            "Executable": mame_executable,
                            "IniPath": mame_ini_path
                        }
                    )
                    
                # Wait a moment for MAME to start
                time.sleep(5)
                
                # Attempt to refocus MAME window from Python side as well
                refocus_mame(rom)
                
                log_message("MAME launch process completed", "MAME")
                return True
                
            finally:
                # Return to the original directory
                os.chdir(current_dir)
        else:
            # For non-Windows platforms, implement direct launching
            log_message("Direct MAME launching on non-Windows platforms not implemented yet", "MAME")
            return False
            
    except Exception as e:
        log_message(f"Failed to launch MAME: {str(e)}", "MAME")
        return False

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python launch_mame.py <rom> [save_state]")
        sys.exit(1)
    
    rom = sys.argv[1]
    save_state = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Launch MAME
    success = launch_mame(rom, save_state)
    sys.exit(0 if success else 1) 