"""
Core Functions Module for Arcade Station.

This module contains essential utilities and functions used throughout the Arcade Station
application. It handles configuration loading, process management, platform detection,
and common operations that need to be accessible across the codebase.

The functions in this module are designed to be platform-agnostic where possible,
with platform-specific implementations when necessary.
"""

import os
import logging
import tomllib
import platform
import subprocess
import psutil
import keyboard
import sys
import time

# function Invoke-SetMarqueeFromFile
# function Open-FullscreenImage
# function Send-Keystrokes
# function Set-ForegroundWindow
# function Start-Sound

def open_header(script_name):
    """
    Prepare the environment for script execution and initialize logging.
    
    Sets up global variables for logging and exit codes, loads configuration,
    and establishes the logging infrastructure. This should typically be
    called at the beginning of each script.
    
    Args:
        script_name: String identifier for the calling script, used in log files.
        
    Returns:
        None. Sets global variables for use throughout the script.
    """
    # Determine the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load configuration from default_config.toml
    config = load_toml_config('default_config.toml')
    log_folder_path = config['logging']['logdirectory']

    # Determine the calling script name programmatically
    if not script_name:
        script_name = "UnknownScript"

    # Log the invoking script
    log_message(f"Script invoked: {script_name}", "MENU")

    # Define other script-level variables
    global exit_code, log_file_path, log_tail_path
    exit_code = -1
    log_file_path = os.path.join(log_folder_path, f"{script_name}.log")
    log_tail_path = os.path.join(log_folder_path, f"{script_name}_Transcript.log")

    # Create our log folder directory if it doesn't exist
    if not os.path.exists(log_folder_path):
        os.makedirs(log_folder_path)

    # Initialize logging
    logging.basicConfig(filename=log_file_path, level=logging.INFO)
    logging.info(f"Header opened for script: [{script_name}]")

def determine_operating_system():
    """
    Detect the current operating system.
    
    Returns:
        str: The detected operating system - 'Windows', 'Linux', 'Darwin' (macOS),
            or 'Unknown' if the platform cannot be determined.
    """
    return platform.system()

def convert_path_for_platform(path):
    """
    Convert file paths to be compatible with the current operating system.
    
    Transforms forward slashes to backslashes on Windows and vice versa
    on Unix-like systems to ensure cross-platform compatibility of paths.
    
    Args:
        path (str): The file path to convert.
        
    Returns:
        str: The converted path appropriate for the current platform.
             Returns unchanged if path is None.
    """
    if not path:
        return path
        
    # Convert slashes based on current OS
    os_type = platform.system()
    if os_type == "Windows":
        # Replace forward slashes with backslashes for Windows
        return path.replace('/', '\\')
    else:
        # Replace backslashes with forward slashes for Unix-like systems
        return path.replace('\\', '/')

def load_toml_config(file_name):
    """
    Load configuration from a specified TOML file in the config directory.
    
    Locates the configuration file relative to the application structure
    and parses its contents into a Python dictionary.
    
    Args:
        file_name (str): The name of the TOML configuration file.
    
    Returns:
        dict: Dictionary containing the configuration from the TOML file.
        
    Raises:
        FileNotFoundError: If the specified configuration file doesn't exist.
        tomllib.TOMLDecodeError: If the TOML file has invalid syntax.
    """
    # Determine the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Calculate the base path relative to the script's directory
    # Adjust the number of '..' based on the new location of the script
    base_path = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..', 'config'))
    config_path = os.path.join(base_path, file_name)
    
    with open(config_path, 'rb') as file:
        return tomllib.load(file)

def load_key_mappings_from_toml(toml_file_path):
    """
    Load keyboard shortcut mappings from a specified TOML configuration file.
    
    Parses the TOML file and extracts keyboard shortcuts and their associated
    actions, logging the results for debugging purposes.
    
    Args:
        toml_file_path (str): Path to the TOML file containing key mappings.
    
    Returns:
        dict: A dictionary where keys are keyboard shortcuts and values are 
             the corresponding actions to execute.
    """
    config = load_toml_config(toml_file_path)
    log_message(f"Loaded key mappings config: {config}", "MENU")

    # Retrieve the key-action mappings
    key_mappings = config.get('key_mappings', {})
    
    if not key_mappings:
        log_message("No key mappings found in the TOML file.", "MENU")
    
    return key_mappings

def start_listening_to_keybinds_from_toml(toml_file_path):
    """
    Set up keyboard shortcut listeners based on mappings in a TOML file.
    
    Registers hotkeys that trigger either application launches or the
    kill processes functionality. Runs indefinitely until interrupted.
    
    Args:
        toml_file_path (str): Path to the TOML file containing key mappings.
        
    Note:
        This function blocks execution until interrupted with Ctrl+C.
    """
    # Load key mappings from the TOML file
    key_mappings = load_key_mappings_from_toml(toml_file_path)
    log_message(f"Loaded key mappings: {key_mappings}", "MENU")

    # Register hotkeys based on the mappings
    for hotkey, action in key_mappings.items():
        # Resolve the action path relative to the base directory
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        action_path = os.path.abspath(os.path.join(base_dir, action))
        
        if action == "kill_processes":
            script_path = os.path.join(os.path.dirname(__file__), 'kill_all_and_reset_pegasus.py')
            keyboard.add_hotkey(hotkey, lambda: subprocess.Popen(['python', script_path]))
        else:
            keyboard.add_hotkey(hotkey, lambda action_path=action_path: start_app(action_path))

    log_message("Listener started. Press Ctrl+C to stop.", "MENU")
    try:
        # Block forever, waiting for hotkeys
        keyboard.wait()
    except KeyboardInterrupt:
        log_message("Listener stopped.", "MENU")

def kill_processes_from_toml(toml_file_path):
    """
    Terminate processes listed in a TOML configuration file.
    
    Reads process identifiers from the specified configuration file
    and attempts to terminate each one, logging the results.
    
    Args:
        toml_file_path (str): Path to the TOML file containing process identifiers.
        
    Returns:
        None
    """

    log_message("Loading processes to kill...", "MENU")
    config = load_toml_config(toml_file_path)
    log_message(f"Loaded config: {config}", "MENU")

    processes_to_kill = config.get('processes', {}).get('names', [])
    if not processes_to_kill:
        log_message("No processes found to kill in the TOML file.", "MENU")
        return
    
    # Make all process names case insensitive for comparison
    processes_to_kill = [proc.casefold() for proc in processes_to_kill]
    
    # Append .exe for Windows if needed
    if platform.system() == "Windows":
        processes_to_kill = [proc if proc.endswith('.exe') else f"{proc}.exe" for proc in processes_to_kill]

    for proc in psutil.process_iter(['name']):
        try:
            process_name = proc.info['name'].lower()
            if process_name in processes_to_kill:
                log_message(f"Killing process: {proc.info['name']}", "MENU")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            log_message(f"Error handling process {proc.info['name']}: {e}", "MENU")

def load_installed_games():
    """
    Load the configuration of installed games from the TOML configuration.
    
    Retrieves the list of installed games and their associated paths and 
    configuration from the pegasus_binaries.toml file.
    
    Returns:
        dict: Dictionary containing configuration for installed games and applications.
    """
    return load_toml_config('pegasus_binaries.toml')

def get_pegasus_binary(installed_games):
    """
    Determine the appropriate Pegasus frontend executable for the current OS.
    
    Uses platform detection to select the correct binary path from the
    installed_games configuration, based on the operating system.
    
    Args:
        installed_games (dict): Dictionary containing paths to Pegasus binaries
                               for different operating systems.
    
    Returns:
        str: Absolute path to the appropriate Pegasus binary for the current OS.
    """
    config = load_toml_config('default_config.toml')
    
    # First try to find pegasus-fe in a relative path (installed environment)
    # Try different possible locations
    potential_paths = [
        # Standard installed location
        os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../pegasus-fe')),
        # Alternative installed location (one level up)
        os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../pegasus-fe')),
        # Directly in the same directory as the executable
        os.path.abspath(os.path.join(os.path.dirname(sys.executable), 'pegasus-fe'))
    ]
    
    pegasus_base_path = None
    for path in potential_paths:
        if os.path.exists(path):
            pegasus_base_path = path
            log_message(f"Found Pegasus base path: {pegasus_base_path}", "GAME")
            break
    
    if not pegasus_base_path:
        log_message("Could not find Pegasus base path in any expected location", "GAME")
        # Default to the original path as a fallback
        pegasus_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../pegasus-fe'))
    
    os_type = platform.system()
    if os_type == "Windows":
        binary_path = os.path.join(pegasus_base_path, installed_games['pegasus']['windows_binary'])
    elif os_type == "Darwin":
        binary_path = os.path.join(pegasus_base_path, installed_games['pegasus']['mac_binary'])
    else:
        binary_path = os.path.join(pegasus_base_path, installed_games['pegasus']['linux_binary'])
    
    log_message(f"Resolved Pegasus binary path: {binary_path}", "GAME")
    return binary_path

def start_pegasus():
    """
    Launch the Pegasus frontend application.
    
    Retrieves the appropriate binary path for the current operating system
    and launches the Pegasus frontend. Logs the outcome of the launch attempt.
    
    Returns:
        bool: True if Pegasus was launched successfully, False otherwise
    """
    try:
        installed_games = load_installed_games()
        pegasus_binary = get_pegasus_binary(installed_games)
        
        if not os.path.exists(pegasus_binary):
            log_message(f"Binary not found: {pegasus_binary}", "GAME")
            
            # Check if we can find the binary manually
            os_type = platform.system()
            binary_name = ""
            if os_type == "Windows":
                binary_name = installed_games['pegasus']['windows_binary']
            elif os_type == "Darwin":
                binary_name = installed_games['pegasus']['mac_binary']
            else:
                binary_name = installed_games['pegasus']['linux_binary']
            
            log_message(f"Searching for binary with name: {binary_name}", "GAME")
            
            # Try to locate the binary in common locations
            possible_locations = [
                os.path.abspath("."),  # Current directory
                os.path.abspath(".."),  # Parent directory
                os.path.dirname(sys.executable),  # Directory of the Python executable
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),  # Up one level from current file
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),  # Up two levels
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")),  # Up three levels
            ]
            
            for location in possible_locations:
                for root, dirs, files in os.walk(location):
                    if binary_name in files:
                        found_binary = os.path.join(root, binary_name)
                        log_message(f"Found binary at: {found_binary}", "GAME")
                        pegasus_binary = found_binary
                        break
                    # Check if pegasus-fe directory exists in this location
                    if "pegasus-fe" in dirs:
                        pegasus_dir = os.path.join(root, "pegasus-fe")
                        possible_binary = os.path.join(pegasus_dir, binary_name)
                        if os.path.exists(possible_binary):
                            log_message(f"Found binary in pegasus-fe dir: {possible_binary}", "GAME")
                            pegasus_binary = possible_binary
                            break
                if os.path.exists(pegasus_binary):
                    break
            
            # If still not found, return False
            if not os.path.exists(pegasus_binary):
                log_message("Failed to find Pegasus binary after extensive search", "GAME")
                return False
        
        # Try to launch Pegasus with absolute path and working directory
        log_message(f"Starting Pegasus with binary [{pegasus_binary}]...", "GAME")
        
        # Get the directory of the binary to use as working directory
        working_dir = os.path.dirname(pegasus_binary)
        log_message(f"Using working directory: {working_dir}", "GAME")
        
        # Launch with explicit working directory and full path
        process = subprocess.Popen(
            pegasus_binary, 
            shell=True,
            cwd=working_dir
        )
        
        # Brief pause to let process start
        time.sleep(1)
        
        # Check if process is running
        if process.poll() is None:
            log_message("Pegasus process started successfully", "GAME")
            return True
        else:
            log_message(f"Pegasus process exited immediately with code: {process.returncode}", "GAME")
            
            # Try alternative launch method
            log_message("Trying alternative launch method...", "GAME")
            if os.name == 'nt':  # Windows
                try:
                    os.startfile(pegasus_binary)
                    log_message("Launched using os.startfile", "GAME")
                    return True
                except Exception as e:
                    log_message(f"Failed to launch with os.startfile: {e}", "GAME")
            
            return False
            
    except Exception as e:
        log_message(f"Failed to start Pegasus: {e}", "GAME")
        import traceback
        log_message(traceback.format_exc(), "GAME")
        return False

def start_app(executable_path):
    """
    Launch an application based on its executable path.
    
    Handles different types of executables (PowerShell scripts, VBScripts, 
    batch files, and regular executables) with appropriate launching methods 
    based on the operating system.
    
    Args:
        executable_path (str): Path to the executable or script to launch.
        
    Returns:
        None
        
    Note:
        PowerShell scripts, VBScripts, and batch files are only supported 
        on Windows systems.
    """
    try:
        os_type = determine_operating_system()
        log_message(f"Starting process [{executable_path}] on {os_type}...", "MENU")

        # Check if the file is a PowerShell script
        if executable_path.endswith('.ps1'):
            if os_type == "Windows":
                # Use PowerShell to execute the script
                subprocess.Popen(['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', executable_path])
            else:
                log_message("PowerShell scripts are not supported on non-Windows systems.", "MENU")
        # Check if the file is a batch file
        elif executable_path.endswith('.bat') or executable_path.endswith('.cmd'):
            if os_type == "Windows":
                # Use cmd to execute the batch file with admin privileges if available
                log_message(f"Launching batch file: {executable_path}", "MENU")
                try:
                    # Try to run as admin for full system access
                    subprocess.Popen(['powershell.exe', '-ExecutionPolicy', 'Bypass', 
                                    '-Command', f"Start-Process -FilePath '{executable_path}' -Verb RunAs"])
                except Exception as batch_error:
                    log_message(f"Failed to launch batch file with admin rights: {batch_error}", "MENU")
                    # Fallback - run directly
                    subprocess.Popen([executable_path], shell=True)
            else:
                log_message("Batch files are not supported on non-Windows systems.", "MENU")
        # Check if the file is a VBScript
        elif executable_path.endswith('.vbs'):
            if os_type == "Windows":
                # Use Windows Script Host to run VBScript invisibly
                # The 0 parameter means "hide the window"
                subprocess.Popen(['wscript.exe', executable_path], creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                log_message("VBScript is not supported on non-Windows systems.", "MENU")
        else:
            # Logic to handle different operating systems for other executables
            if os_type == "Windows":
                # Log additional details for debugging
                log_message(f"Launching Windows executable with shell=True: {executable_path}", "MENU_DEBUG")
                subprocess.Popen(f'start "" "{executable_path}"', shell=True)
            elif os_type == "Darwin":
                subprocess.Popen(['open', executable_path])
            else:
                subprocess.Popen(['xdg-open', executable_path])
                
        log_message(f"Launched process [{executable_path}].", "MENU")
    except Exception as e:
        log_message(f"Failed to start process: {e}", "MENU")

def kill_process_by_identifier(identifier):
    """
    Terminate a process and its children based on an identifier string.
    
    Searches for processes with command line arguments matching the provided
    identifier or its predefined patterns. Once found, terminates the process
    and all its child processes.
    
    Args:
        identifier (str): The identifier to search for in process command lines.
                          Can be a predefined key ('marquee_image', 'open_image', 
                          'start_pegasus') or any custom string.
    
    Returns:
        bool: True if any processes were found and killed, False otherwise.
        
    Note:
        Predefined identifiers map to specific command-line patterns for common
        processes in the Arcade Station application.
    """
    log_message(f"Searching for processes with identifier: {identifier}", "MENU")
    killed = False
    
    # Map standard identifiers to specific command-line patterns
    identifier_patterns = {
        "marquee_image": ["--identifier=marquee_image"],
        "open_image": ["--identifier=marquee_image"],  # For backward compatibility, point to new ID
        "start_pegasus": ["--identifier=start_pegasus"]
    }
    
    # Get the patterns to look for
    patterns = identifier_patterns.get(identifier, [identifier])
    
    for proc in psutil.process_iter(attrs=["pid", "name", "cmdline"]):
        try:
            cmdline = proc.info["cmdline"]
            if cmdline and any(any(pattern in arg for arg in cmdline) for pattern in patterns):
                log_message(f"Found process {proc.pid} with cmdline: {cmdline}", "MENU")
                # First, kill any children of this process.
                children = proc.children(recursive=True)
                for child in children:
                    log_message(f"Terminating child process {child.pid}", "MENU")
                    child.kill()
                # Now kill the process itself.
                log_message(f"Terminating process {proc.pid}", "MENU")
                proc.kill()
                proc.wait(timeout=5)
                killed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            log_message(f"Error processing process {proc.pid}: {e}", "MENU")
            continue
    
    if not killed:
        log_message(f"No processes found with identifier: {identifier}", "MENU")
    
    return killed

def launch_script(script_path, identifier=None, extra_args=None):
    """
    Launch a Python script using the virtual environment's Python interpreter.
    
    Creates a subprocess running the specified Python script with optional
    identifier and additional arguments. The identifier helps with process
    management and can be used to find and terminate the process later.
    
    Args:
        script_path (str): Path to the Python script to be executed.
        identifier (str, optional): Identifier tag to append to the command line.
                                   Used for process tracking and management.
        extra_args (list, optional): List of additional command-line arguments
                                    to pass to the script.
    
    Returns:
        subprocess.Popen: The process object for the launched script.
        
    Note:
        Uses the Python executable from the virtual environment.
    """
    # Use the current Python executable instead of hardcoding the path
    python_executable = sys.executable
    log_message(f"Using Python executable: {python_executable}", "SCRIPT")
    
    # Build the command-line arguments.
    args = [python_executable, script_path]
    if extra_args:
        args.extend(extra_args)
    if identifier:
        args.append(f"--identifier={identifier}")
    
    # Windows-specific options: hide the console window.
    if os.name == 'nt':
        creationflags = subprocess.CREATE_NO_WINDOW
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # 0 means SW_HIDE.
    else:
        creationflags = 0
        startupinfo = None

    log_message(f"Launching script: {' '.join(args)}", "SCRIPT")
    process = subprocess.Popen(
        args,
        creationflags=creationflags,
        startupinfo=startupinfo
    )
    return process

# Function to kill Pegasus process
def kill_pegasus():
    """
    Terminate the Pegasus frontend process.
    
    Identifies and terminates Pegasus frontend processes based on 
    platform-specific executable names. Handles platform detection
    automatically to target the correct process name.
    
    Returns:
        None
        
    Note:
        Supported platforms include Windows ('win32'), macOS ('darwin'), 
        and Linux ('linux'). Logs an error for unsupported platforms.
    """
    # Define the process names for Pegasus on different platforms
    pegasus_process_names = {
        'win32': ['pegasus-fe_windows', 'pegasus-fe_windows.exe'],
        'darwin': ['pegasus-fe_mac'],
        'linux': ['pegasus-fe_linux']
    }

    # Get the current platform
    platform_name = sys.platform

    # Determine the process names based on the platform
    process_names = pegasus_process_names.get(platform_name, [])

    if not process_names:
        log_message(f"Unsupported platform: {platform_name}", "GAME")
        return

    # Iterate over all running processes
    for proc in psutil.process_iter(['name']):
        try:
            # Check if the process name matches any of the Pegasus names
            if proc.info['name'].lower() in (name.lower() for name in process_names):
                log_message(f"Killing process: {proc.info['name']}", "GAME")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            log_message(f"Error handling process {proc.info['name']}: {e}", "GAME")

def start_process(file_path):
    """
    Start a process in a platform-appropriate way.
    
    Launches executables, scripts, or applications using the method
    appropriate for the current operating system. Handles different
    file types accordingly.
    
    Args:
        file_path (str): The path to the executable, script, or application to run.
        
    Returns:
        None
        
    Note:
        For Windows, uses os.startfile for .exe files and subprocess for others.
        For macOS, uses the 'open' command.
        For Linux, uses 'xdg-open' for GUI applications or direct execution.
    """
    os_type = sys.platform

    try:
        if os_type.startswith('win'):
            # Windows: Use startfile or subprocess
            if file_path.endswith('.exe'):
                os.startfile(file_path)
            else:
                subprocess.Popen(['python', file_path], shell=True)
        elif os_type.startswith('darwin'):
            # macOS: Use open command
            subprocess.Popen(['open', file_path])
        elif os_type.startswith('linux'):
            # Linux: Use xdg-open or execute directly
            if os.access(file_path, os.X_OK):
                subprocess.Popen([file_path])
            else:
                subprocess.Popen(['xdg-open', file_path])
        else:
            raise Exception(f"Unsupported platform: {os_type}")

        log_message(f"Started process for: {file_path}", "MENU")
    except Exception as e:
        log_message(f"Failed to start process for {file_path}: {e}", "MENU")

def load_game_config():
    """
    Load game configuration from the installed_games.toml file.
    
    Retrieves detailed configuration for games and applications installed
    in the Arcade Station system.
    
    Returns:
        dict: Dictionary containing installed game configurations.
    """
    return load_toml_config('installed_games.toml')

def load_mame_config():
    """
    Load MAME emulator configuration from the mame_config.toml file.
    
    Retrieves settings specific to the MAME arcade emulator,
    including ROM paths, configuration options, and launch parameters.
    
    Returns:
        dict: Dictionary containing MAME configuration settings.
    """
    return load_toml_config('mame_config.toml')

def run_powershell_script(script_path, params=None):
    """
    Execute a PowerShell script with optional parameters.
    
    Runs a PowerShell script with hidden window style and bypassed execution policy.
    Supports passing named parameters to the script and captures output.
    
    Args:
        script_path (str): Path to the PowerShell script file (.ps1).
        params (dict, optional): Dictionary of parameter names and values
                               to pass to the PowerShell script.
        
    Returns:
        subprocess.Popen: The process object for the PowerShell script execution,
                         or None if an error occurred.
                         
    Note:
        This function is Windows-specific and will fail on other operating systems.
        The PowerShell window is hidden from view during execution.
    """
    # Construct the command
    command = ['powershell.exe', '-WindowStyle', 'Hidden', '-ExecutionPolicy', 'Bypass', '-File', script_path]
    
    # Add parameters if provided
    if params:
        for key, value in params.items():
            command.extend([f'-{key}', f'{value}'])
    
    # Create a full command string for logging
    full_command = ' '.join(command)
    log_message(f"Running PowerShell script: {script_path} with params: {params}", "PS")
    log_message(f"Full command: {full_command}", "PS_COMMAND")
    
    try:
        # Run the command
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        return process
    except Exception as e:
        log_message(f"Error running PowerShell script: {e}", "PS")
        return None

def start_process_with_powershell(file_path, working_dir=None, arguments=None):
    """
    Launch a process silently using PowerShell to hide console windows.
    
    Uses PowerShell to start a process in a way that prevents console windows
    from appearing, even for command-line applications. Supports specifying
    a working directory and command-line arguments.
    
    Args:
        file_path (str): Path to the executable or application to launch.
        working_dir (str, optional): Working directory for the process.
        arguments (str, optional): Command-line arguments to pass to the application.
        
    Returns:
        bool: True if the process was started successfully, False otherwise.
        
    Note:
        This function is Windows-specific and relies on PowerShell.
    """
    # Get the path to the PowerShell module
    ps_module_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'windows', 'core_functions.psm1'
    ))
    
    # Construct the PowerShell command
    ps_command = f"Import-Module '{ps_module_path}'; "
    ps_command += f"Start-ProcessSilently -FilePath '{file_path}'"
    
    if working_dir:
        ps_command += f" -WorkingDirectory '{working_dir}'"
    
    if arguments:
        ps_command += f" -Arguments '{arguments}'"
    
    # Log detailed information about what's being executed
    log_message(f"Starting process using PowerShell: {file_path}", "PS")
    log_message(f"Working directory: {working_dir}", "PS_DETAIL")
    log_message(f"Arguments: {arguments}", "PS_DETAIL")
    log_message(f"PowerShell command: {ps_command}", "PS_COMMAND")
    
    try:
        # Execute the PowerShell command
        process = subprocess.Popen(
            ['powershell.exe', '-WindowStyle', 'Hidden', '-ExecutionPolicy', 'Bypass', '-Command', ps_command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        log_message(f"Successfully started process: {file_path}", "PS")
        return True
    except Exception as e:
        log_message(f"Failed to start process using PowerShell: {e}", "PS")
        return False

def log_message(message, prefix=""):
    """
    Log a message to both the console and log file with timestamp.
    
    Creates a formatted log entry with an optional category prefix and timestamp,
    then writes it to both the Python logging system and a dedicated log file
    if one has been configured by open_header().
    
    Args:
        message (str): The message to log.
        prefix (str, optional): A category prefix to add to the message for easier
                               filtering and identification (e.g., "MENU", "GAME").
                               Defaults to an empty string.
    
    Returns:
        None
        
    Note:
        This function requires open_header() to be called first to initialize
        the log file path. If no log file is configured, it will only log to
        the console through Python's logging system.
    """
    try:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Format the message with timestamp and prefix
        if prefix:
            formatted_message = f"[{timestamp}] [{prefix}] {message}"
        else:
            formatted_message = f"[{timestamp}] {message}"
        
        # Log to console (redirect through logging)
        logging.info(formatted_message)
        
        # Also log to the log file if it exists
        if 'log_file_path' in globals() and os.path.exists(os.path.dirname(log_file_path)):
            with open(log_file_path, 'a', encoding='utf-8') as f:
                f.write(formatted_message + '\n')
                
    except Exception as e:
        logging.error(f"Failed to write to log file: {e}")