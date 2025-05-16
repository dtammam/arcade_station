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

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))
sys.path.insert(0, project_root)

from arcade_station.core.common.core_functions import log_message, kill_pegasus
from arcade_station.core.common.kill_all import main as kill_all_processes

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
"""
    
    # Write the script to disk
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make the script executable on Linux/macOS
    if platform.system() != "Windows":
        os.chmod(script_path, 0o755)
    
    return script_path

def main():
    """Kill all Arcade Station processes and then terminate all Python processes."""
    
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