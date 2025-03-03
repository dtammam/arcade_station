"""
Module for managing iCloud photo uploads and services.

This module provides functionality to restart iCloud services on Windows and
manage the upload directory. It runs as a background thread, periodically
restarting iCloud services and cleaning the upload directory.
"""
import os
import sys
import time
import subprocess
import threading

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.abspath(os.path.join(script_dir, '..', '..'))
project_root = os.path.abspath(os.path.join(base_dir, '..'))
sys.path.insert(0, project_root)

from arcade_station.core.common.core_functions import (
    log_message,
    load_toml_config
)

# Import Windows-specific modules for focus management
if sys.platform == "win32":
    try:
        import ctypes
        has_focus_modules = True
    except ImportError:
        has_focus_modules = False
        log_message("Windows focus modules not available", "ICLOUD")
else:
    has_focus_modules = False

def restart_process(process_name, process_path):
    """
    Stop and restart a Windows process.
    
    Args:
        process_name (str): Name of the process to restart (without .exe)
        process_path (str): Path to the directory containing the process executable
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        log_message(f"Attempting to stop process: {process_name}", "ICLOUD")
        
        # Try to terminate the process gracefully with hidden window
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE
        
        # Use more precise targeting to minimize disruption
        subprocess.run(['taskkill', '/F', '/IM', f"{process_name}.exe"], 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                      startupinfo=startupinfo)
        
        # Give it time to shut down
        time.sleep(1)
        
        # Start the process
        full_path = os.path.join(process_path, f"{process_name}.exe")
        log_message(f"Starting process: {full_path}", "ICLOUD")
        
        if not os.path.exists(full_path):
            log_message(f"Process executable not found: {full_path}", "ICLOUD")
            return False
            
        # Ensure the process starts with minimal UI disruption
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE
        
        # Use a lower priority for starting
        if has_focus_modules and sys.platform == "win32":
            # Start with BELOW_NORMAL priority to reduce focus disruption
            subprocess.Popen([full_path], startupinfo=startupinfo, 
                            creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        else:
            subprocess.Popen([full_path], startupinfo=startupinfo)
            
        log_message(f"Successfully started {process_name}", "ICLOUD")
        return True
    except Exception as e:
        log_message(f"Error restarting process {process_name}: {e}", "ICLOUD")
        return False

def clean_directory(directory, delete_files=True):
    """
    Clean a directory by deleting all files.
    
    Args:
        directory (str): Path to the directory to clean
        delete_files (bool): Whether to delete files or just count them
    
    Returns:
        int: Number of files deleted or would have been deleted
    """
    if not delete_files:
        log_message(f"File deletion disabled, skipping cleanup of {directory}", "ICLOUD")
        return 0
        
    try:
        if not os.path.exists(directory):
            log_message(f"Upload directory does not exist: {directory}", "ICLOUD")
            return 0
            
        log_message(f"Cleaning directory: {directory}", "ICLOUD")
        count = 0
        
        for root, _, files in os.walk(directory):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
                    log_message(f"Deleted file: {file_path}", "ICLOUD")
                    count += 1
                except Exception as e:
                    log_message(f"Failed to delete {file}: {e}", "ICLOUD")
        
        log_message(f"Deleted {count} files from {directory}", "ICLOUD")
        return count
    except Exception as e:
        log_message(f"Error cleaning directory {directory}: {e}", "ICLOUD")
        return 0

def icloud_manager():
    """
    Main function to manage iCloud processes and files.
    
    This function runs in an infinite loop, periodically:
    1. Restarting specified iCloud service processes
    2. Waiting for a defined interval to allow uploads to complete
    3. Cleaning the upload directory (optionally deleting files)
    
    Configuration is read from screenshot_config.toml [icloud_upload] section.
    """
    log_message("Starting iCloud manager", "ICLOUD")
    
    # Load configuration using the standard function
    config = load_toml_config('screenshot_config.toml')
    if not config or 'icloud_upload' not in config:
        log_message("Failed to load iCloud configuration, exiting", "ICLOUD")
        return
    
    icloud_config = config['icloud_upload']
    
    # Extract configuration values
    apple_services_path = icloud_config.get('apple_services_path', 
                                      r"C:\Program Files (x86)\Common Files\Apple\Internet Services")
    processes_to_restart = icloud_config.get('processes_to_restart', 
                                     ["iCloudServices", "iCloudPhotos"])
    upload_directory = icloud_config.get('upload_directory', 
                                 r"C:\Users\me\Pictures\Uploads")
    interval_seconds = int(icloud_config.get('interval_seconds', 360))
    delete_after_upload = icloud_config.get('delete_after_upload', True)
    
    # Use a minimum safe interval
    minimum_interval = 300  # 5 minutes
    if interval_seconds < minimum_interval:
        log_message(f"Interval too short ({interval_seconds}s), setting to {minimum_interval}s", "ICLOUD")
        interval_seconds = minimum_interval
    
    # Log configuration
    log_message("iCloud manager configuration:", "ICLOUD")
    log_message(f"  Apple Services Path: {apple_services_path}", "ICLOUD")
    log_message(f"  Processes to restart: {processes_to_restart}", "ICLOUD")
    log_message(f"  Upload directory: {upload_directory}", "ICLOUD")
    log_message(f"  Interval: {interval_seconds} seconds", "ICLOUD")
    log_message(f"  Delete after upload: {delete_after_upload}", "ICLOUD")
    
    # For detecting game activity to avoid interruptions
    last_cycle_time = time.time() - interval_seconds  # Allow immediate first run
    
    # Main loop
    while True:
        try:
            # Check if enough time has passed since last cycle
            current_time = time.time()
            time_since_last = current_time - last_cycle_time
            
            if time_since_last < interval_seconds:
                # Not time for a cycle yet, sleep for a bit and check again
                time.sleep(min(10, interval_seconds - time_since_last))
                continue
            
            # Check if any game processes are currently active (avoid interrupting gameplay)
            game_active = False
            try:
                if sys.platform == "win32":
                    # Check for common game processes
                    import psutil
                    game_processes = ["mame", "game.exe", "steam.exe", "retroarch.exe"]
                    for proc in psutil.process_iter(['name']):
                        proc_name = proc.info['name'].lower()
                        if any(game in proc_name for game in game_processes):
                            log_message(f"Game process detected ({proc_name}), deferring iCloud cycle", "ICLOUD")
                            game_active = True
                            break
            except Exception as e:
                log_message(f"Error checking for game processes: {e}", "ICLOUD")
                
            if game_active:
                # Games are active, sleep and try again later
                time.sleep(60)  # Check again in a minute
                continue
                
            # Save the current foreground window before performing operations
            foreground_hwnd = None
            if has_focus_modules:
                try:
                    foreground_hwnd = ctypes.windll.user32.GetForegroundWindow()
                    log_message("Saved current foreground window handle for later restoration", "ICLOUD")
                except Exception as e:
                    log_message(f"Failed to get foreground window: {e}", "ICLOUD")
            
            log_message("Starting processing cycle", "ICLOUD")
            
            # Update last cycle time
            last_cycle_time = time.time()
            
            # Restart each process
            for process in processes_to_restart:
                restart_process(process, apple_services_path)
                time.sleep(1)  # Give a short delay between process restarts
            
            # Wait for a shorter interval during this cycle since we already waited
            wait_time = min(120, interval_seconds // 3)  # No more than 2 minutes
            log_message(f"Waiting {wait_time} seconds before cleaning directory", "ICLOUD")
            time.sleep(wait_time)
            
            # Clean the upload directory
            deleted_count = clean_directory(upload_directory, delete_after_upload)
            log_message(f"Deleted {deleted_count} files", "ICLOUD")
            
            # Restore focus to the original window if possible
            if has_focus_modules and foreground_hwnd:
                try:
                    # Restore the original foreground window
                    ctypes.windll.user32.SetForegroundWindow(foreground_hwnd)
                    
                    # Force Windows to refresh focus by simulating Alt key press
                    ALT_KEY = 0x12
                    KEYEVENTF_KEYUP = 0x0002
                    ctypes.windll.user32.keybd_event(ALT_KEY, 0, 0, 0)  # Alt press
                    time.sleep(0.1)
                    ctypes.windll.user32.keybd_event(ALT_KEY, 0, KEYEVENTF_KEYUP, 0)  # Alt release
                    
                    log_message("Restored original window focus", "ICLOUD")
                except Exception as e:
                    log_message(f"Failed to restore window focus: {e}", "ICLOUD")
            
            log_message("Processing cycle completed", "ICLOUD")
            
        except Exception as e:
            log_message(f"Error in processing cycle: {e}", "ICLOUD")
            # Sleep for a bit before trying again
            time.sleep(30)

def start_icloud_manager_thread():
    """
    Start the iCloud manager in a background thread.
    
    This function creates a daemon thread that runs the iCloud manager process.
    The thread will automatically terminate when the main program exits.
    
    Returns:
        bool: True if the thread was started successfully, False otherwise
    """
    try:
        # Create and start daemon thread
        thread = threading.Thread(target=icloud_manager, daemon=True)
        thread.start()
        log_message(f"Started iCloud manager thread: {thread.name}", "ICLOUD")
        return True
    except Exception as e:
        log_message(f"Failed to start iCloud manager thread: {e}", "ICLOUD")
        return False

if __name__ == "__main__":
    # If run directly, start in the foreground
    icloud_manager() 