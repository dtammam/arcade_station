import os
import logging
import tomllib
import platform
import subprocess
import psutil
import keyboard
import sys

# function Invoke-SetMarqueeFromFile
# function Open-FullscreenImage
# function Send-Keystrokes
# function Set-ForegroundWindow
# function Start-Sound

def open_header(script_name):
    """
    Prepares global variables that will be used for various functions throughout the script.
    Specifically configured for logging locations and exit codes.
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
    Returns the current operating system.
    """
    return platform.system()

def load_toml_config(file_name):
    """
    Load configuration from a specified TOML file.
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
    Load key-action mappings from a specified TOML file.
    
    Args:
        toml_file_path (str): Path to the TOML file containing key mappings.
    
    Returns:
        dict: A dictionary of key-action mappings.
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
    Load key-action mappings from a specified TOML file and start listening for keybinds.
    
    Args:
        toml_file_path (str): Path to the TOML file containing key mappings.
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
    Load the list of processes to kill from a specified TOML file and kill them.
    
    Args:
        toml_file_path (str): Path to the TOML file containing processes to kill.
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
    Load installed games configuration from a TOML file.
    """
    return load_toml_config('pegasus_binaries.toml')

def get_pegasus_binary(installed_games):
    """
    Returns the path to the appropriate Pegasus binary based on the operating system.
    """
    config = load_toml_config('default_config.toml')
    # Adjust the base path to point directly to the pegasus-fe directory
    pegasus_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../pegasus-fe'))
    
    os_type = platform.system()
    if os_type == "Windows":
        binary_path = os.path.join(pegasus_base_path, installed_games['pegasus']['windows_binary'])
    elif os_type == "Darwin":
        binary_path = os.path.join(pegasus_base_path, installed_games['pegasus']['mac_binary'])
    else:
        binary_path = os.path.join(pegasus_base_path, installed_games['pegasus']['linux_binary'])
    
    print(f"Constructed binary path: {binary_path}")
    return binary_path

def start_pegasus():
    """
    Function to start the Pegasus application.
    """
    installed_games = load_installed_games()
    pegasus_binary = get_pegasus_binary(installed_games)
    
    if not os.path.exists(pegasus_binary):
        log_message(f"Binary not found: {pegasus_binary}", "GAME")
        return

    try:
        log_message(f"Starting Pegasus with binary [{pegasus_binary}]...", "GAME")
        subprocess.Popen(pegasus_binary, shell=True)
        log_message("Pegasus launched.", "GAME")
    except Exception as e:
        log_message(f"Failed to start Pegasus: {e}", "GAME")

def start_app(executable_path):
    """
    Function to start an application given its executable path.
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
        else:
            # Logic to handle different operating systems for other executables
            if os_type == "Windows":
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
    Kill a process by its identifier.
    
    The identifier can be either a standard name (like 'marquee_image') or 
    any part of the command line used to start the process.
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
    Launch a Python script from your virtual environment.
    
    If an identifier is provided, it is appended as a command-line argument 
    (e.g. '--identifier=open_image') so that external scripts can find this process.
    Any extra_args is a list of additional command-line arguments.
    """
    # Path to your venv's Python executable.
    # TODO: Make this dynamic.
    python_executable = r"C:/Repositories/arcade_station/.venv/Scripts/python.exe"
    
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

    process = subprocess.Popen(
        args,
        creationflags=creationflags,
        startupinfo=startupinfo
    )
    return process

# Function to kill Pegasus process
def kill_pegasus():
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
    Start a process based on the file path and the operating system.

    Args:
        file_path (str): The path to the executable or script to run.
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
    """
    return load_toml_config('installed_games.toml')

def load_mame_config():
    """
    Load MAME configuration from the mame_config.toml file.
    """
    return load_toml_config('mame_config.toml')

def log_message(message, prefix=""):
    """
    Simple logging function that prints a message with an optional prefix.
    
    Args:
        message (str): The message to log
        prefix (str): Optional prefix to add to the message
    """
    if prefix:
        print(f"[{prefix}] {message}")
    else:
        print(message)