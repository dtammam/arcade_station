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
        
        # Try to terminate the process gracefully
        subprocess.run(['taskkill', '/F', '/IM', f"{process_name}.exe"], 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                      creationflags=subprocess.CREATE_NO_WINDOW)
        
        # Give it time to shut down
        time.sleep(2)
        
        # Start the process
        full_path = os.path.join(process_path, f"{process_name}.exe")
        log_message(f"Starting process: {full_path}", "ICLOUD")
        
        if not os.path.exists(full_path):
            log_message(f"Process executable not found: {full_path}", "ICLOUD")
            return False
            
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
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
    Restarts iCloud services and cleans upload directory on a schedule.
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
    
    # Validate interval
    if interval_seconds < 10:
        log_message(f"Interval too short ({interval_seconds}s), setting to 300s", "ICLOUD")
        interval_seconds = 300
    
    # Log configuration
    log_message("iCloud manager configuration:", "ICLOUD")
    log_message(f"  Apple Services Path: {apple_services_path}", "ICLOUD")
    log_message(f"  Processes to restart: {processes_to_restart}", "ICLOUD")
    log_message(f"  Upload directory: {upload_directory}", "ICLOUD")
    log_message(f"  Interval: {interval_seconds} seconds", "ICLOUD")
    log_message(f"  Delete after upload: {delete_after_upload}", "ICLOUD")
    
    # Main loop
    while True:
        try:
            log_message("Starting processing cycle", "ICLOUD")
            
            # Restart each process
            for process in processes_to_restart:
                restart_process(process, apple_services_path)
                time.sleep(1)  # Give a short delay between process restarts
            
            # Wait for the specified interval
            log_message(f"Waiting {interval_seconds} seconds before cleaning directory", "ICLOUD")
            time.sleep(interval_seconds)
            
            # Clean the upload directory
            deleted_count = clean_directory(upload_directory, delete_after_upload)
            log_message(f"Deleted {deleted_count} files", "ICLOUD")
            
            log_message("Processing cycle completed", "ICLOUD")
            
        except Exception as e:
            log_message(f"Error in processing cycle: {e}", "ICLOUD")
            # Sleep for a bit before trying again
            time.sleep(30)

def start_icloud_manager_thread():
    """
    Start the iCloud manager in a background thread.
    
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