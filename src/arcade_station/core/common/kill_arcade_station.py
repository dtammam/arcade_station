"""
Kill Arcade Station - Complete Process Termination

This script provides a full reset, killing all Arcade Station processes including
Pegasus frontend and then launching a separate script to terminate all Python processes.

Use this script when you need to completely reset the system and exit Arcade Station
while in PC mode (not kiosk mode).
"""

import sys
import os
import platform
import subprocess

# Add the project root to the Python path - with multiple approaches to find it
script_dir = os.path.dirname(os.path.abspath(__file__))
possible_roots = [
    # Standard path based on script location
    os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..')),
    # Path if running from the installed location
    os.path.abspath(os.path.join(script_dir, '..', '..', '..'))
]

# Try each possible root until we find one that works
arcade_station_found = False
for root in possible_roots:
    sys.path.insert(0, root)
    try:
        # Try to import a module to verify path is correct
        import arcade_station
        arcade_station_found = True
        break
    except ImportError:
        # Remove the path we just added if it didn't work
        sys.path.pop(0)

# If all explicit paths failed, try relative to current working directory
if not arcade_station_found:
    current_dir = os.getcwd()
    sys.path.insert(0, current_dir)
    # Also try adding src directory if it exists
    src_dir = os.path.join(current_dir, 'src')
    if os.path.exists(src_dir):
        sys.path.insert(0, src_dir)

try:
    from arcade_station.core.common.core_functions import log_message, kill_pegasus
    from arcade_station.core.common.kill_all import main as kill_all_processes
except ImportError as e:
    # Fallback logging if import fails
    print(f"ERROR: Could not import required modules: {e}")
    print("Python path:", sys.path)
    
    # Define minimal implementations for required functions
    def log_message(message, category="ERROR"):
        """
        Fallback logging function when core_functions import fails.
        
        Args:
            message (str): The message to log
            category (str): Category for the log message, defaults to "ERROR"
        """
        print(f"[{category}] {message}")
    
    def kill_pegasus():
        """
        Fallback function to kill Pegasus when core_functions import fails.
        
        Attempts to terminate Pegasus processes using taskkill command.
        Handles both .exe and non-.exe process names.
        """
        print("Attempting to kill Pegasus manually...")
        for proc_name in ["pegasus-fe_windows", "pegasus-fe_windows.exe"]:
            try:
                subprocess.run(["taskkill", "/F", "/IM", proc_name], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
    
    def kill_all_processes():
        """
        Fallback function to kill all Arcade Station processes when core_functions import fails.
        
        Attempts to terminate a predefined list of common Arcade Station processes
        using taskkill command. Includes frontend, emulators, and utility processes.
        """
        print("Attempting to kill processes manually...")
        process_names = [
            "cmd.exe", "explorer.exe", "gslauncher.exe", "i_view64.exe", 
            "LightsTest.exe", "mame.exe", "notepad.exe", "pegasus-fe_windows.exe"
        ]
        for proc_name in process_names:
            try:
                subprocess.run(["taskkill", "/F", "/IM", proc_name], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

def create_kill_python_script():
    """
    Create a temporary script that kills all Python processes except itself.
    Returns the path to the created script.
    """
    log_message("Creating kill Python script", "KILL")
    
    # Determine the appropriate script based on platform
    if platform.system() == "Windows":
        script_path = os.path.join(os.environ.get('TEMP', '.'), 'kill_python.ps1')
        script_content = """
# Get current process ID
$currentPID = $PID

# Kill all Python processes except this PowerShell process
Get-Process python*, py* | Where-Object { $_.ProcessName -match 'python|py' } | ForEach-Object {
    Write-Host "Killing Python process: $($_.ProcessName) (PID: $($_.Id))"
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}

Write-Host "All Python processes terminated."

# Start Explorer as the final step
Start-Sleep -Seconds 1
Write-Host "Starting Explorer..."
Start-Process "C:\\Windows\\explorer.exe"
"""
    else:  # Linux and macOS
        script_path = os.path.join('/tmp', 'kill_python.sh')
        script_content = """#!/bin/bash
# Get current process ID
CURRENT_PID=$$

# Kill all Python processes except those related to this script
pids=$(ps aux | grep -E "python|python3" | grep -v grep | awk '{print $2}')
for pid in $pids; do
    echo "Killing Python process: $pid"
    kill -9 $pid 2>/dev/null
done

echo "All Python processes terminated."

# No direct equivalent to explorer.exe on Linux/macOS
"""
    
    # Write the script to disk
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make the script executable on Linux/macOS
    if platform.system() != "Windows":
        os.chmod(script_path, 0o755)
    
    return script_path

def main():
    """
    Main entry point for the Arcade Station termination process.
    
    Executes a complete system reset by:
    1. Killing all standard Arcade Station processes using kill_all_processes()
    2. Specifically terminating the Pegasus frontend
    3. Creating and executing a platform-specific script to kill all Python processes
    4. On Windows, restarts Explorer as the final step
    
    The function handles platform-specific differences between Windows and Unix-like
    systems (Linux/macOS) for process termination.
    
    Returns:
        None. All operations are logged for debugging purposes.
    """
    
    log_message("Starting full Arcade Station termination", "KILL")
    
    # First, kill all running processes using the standard kill_all function
    log_message("Killing all standard processes", "KILL")
    kill_all_processes()
    
    # Specifically kill Pegasus frontend
    log_message("Killing Pegasus frontend", "KILL")
    kill_pegasus()
    
    # Create the kill Python script
    script_path = create_kill_python_script()
    
    # Execute the script to kill all Python processes based on platform
    log_message("Executing script to kill Python processes", "KILL")
    
    if platform.system() == "Windows":
        # On Windows, launch PowerShell to execute the script
        subprocess.Popen(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        # On Linux/macOS
        subprocess.Popen([script_path], start_new_session=True)
    
    log_message("Kill Arcade Station process complete", "KILL")

if __name__ == "__main__":
    main() 