"""
Kill Arcade Station Wrapper

This script serves as a wrapper entry point for terminating Arcade Station.
It's designed to be called directly by the key listener and handles 
elevated permissions and Python path configuration.
"""

import os
import sys
import subprocess
import platform
import time

def launch_explorer():
    """Launch explorer.exe as the final step."""
    if platform.system() == 'Windows':
        try:
            # Give a short delay to ensure other processes have been terminated
            time.sleep(1)
            print("Starting Explorer...")
            subprocess.Popen(["C:\\Windows\\explorer.exe"])
        except Exception as e:
            print(f"Error starting Explorer: {e}")

def main():
    """
    Main entry point for the Arcade Station termination wrapper.
    
    This function orchestrates the termination process with the following steps:
    1. Configures Python path to ensure proper module imports
    2. Checks and requests administrator privileges on Windows if needed
    3. Attempts to execute the main kill script (kill_arcade_station.py)
    4. Falls back to direct process termination if the main script fails
    5. Launches Explorer as the final step on Windows
    
    The function includes multiple fallback mechanisms:
    - Direct script execution if import fails
    - Manual process termination as a last resort
    - PowerShell script for Python process cleanup
    
    Returns:
        None. All operations are logged to console for debugging.
    """
    print("Kill Arcade Station Wrapper")
    print("-------------------------")
    
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))
    
    # Add paths to Python path
    sys.path.insert(0, project_root)
    sys.path.insert(0, os.path.join(project_root, 'src'))
    
    try:
        # Check if running with admin privileges on Windows
        if platform.system() == 'Windows':
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("Requesting administrator privileges...")
                # Re-run the script with admin privileges
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, __file__, None, 1
                )
                return
        
        # Now execute the actual kill script - import directly since we're in the same directory
        from arcade_station.core.common.kill_arcade_station import main as kill_main
        print("Terminating Arcade Station...")
        kill_main()
        
        print("All Arcade Station processes have been terminated.")
        
        # Launch explorer as the final step
        launch_explorer()
        
    except ImportError as e:
        print(f"ERROR: Could not import kill script: {e}")
        print("Trying direct approach...")
        
        # Try to directly execute the kill script
        kill_script_path = os.path.join(script_dir, 'kill_arcade_station.py')
        
        if os.path.exists(kill_script_path):
            # Run the kill script directly
            subprocess.run([sys.executable, kill_script_path], check=False)
            # Launch explorer after the kill script
            launch_explorer()
        else:
            print(f"ERROR: Kill script not found at {kill_script_path}")
            
            # As a last resort, try to kill processes directly
            if platform.system() == 'Windows':
                # Kill common processes
                process_names = [
                    "pegasus-fe_windows.exe", "mame.exe", "ITGmania.exe", 
                    "LightsTest.exe", "i_view64.exe"
                ]
                
                for proc in process_names:
                    try:
                        subprocess.run(["taskkill", "/F", "/IM", proc], 
                                      stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL)
                    except Exception:
                        pass
                
                # Create a PowerShell script that kills Python processes and then launches explorer
                ps_script = """
                Get-Process python*, py* | Where-Object { $_.ProcessName -match 'python|py' } | ForEach-Object {
                    Write-Host "Killing Python process: $($_.ProcessName) (PID: $($_.Id))"
                    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
                }

                Write-Host "All Python processes terminated."
                
                # Start Explorer
                Start-Sleep -Seconds 1
                Write-Host "Starting Explorer..."
                Start-Process "C:\\Windows\\explorer.exe"
                """
                
                subprocess.Popen(
                    ["powershell", "-Command", ps_script],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                # Note: Don't launch explorer here since the PowerShell script will do it

if __name__ == "__main__":
    main() 