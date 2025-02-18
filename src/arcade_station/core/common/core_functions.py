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
    print(f"Script invoked: {script_name}")

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
    print("Loaded key mappings config:", config)

    # Retrieve the key-action mappings
    key_mappings = config.get('key_mappings', {})
    
    if not key_mappings:
        print("No key mappings found in the TOML file.")
    
    return key_mappings

def start_listening_to_keybinds_from_toml(toml_file_path):
    """
    Load key-action mappings from a specified TOML file and start listening for keybinds.
    
    Args:
        toml_file_path (str): Path to the TOML file containing key mappings.
    """
    # Load key mappings from the TOML file
    key_mappings = load_key_mappings_from_toml(toml_file_path)
    print("Loaded key mappings:", key_mappings)  # Debugging line to verify the loaded mappings

    # Register hotkeys based on the mappings
    for hotkey, action in key_mappings.items():
        # Resolve the action path relative to the base directory
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        action_path = os.path.abspath(os.path.join(base_dir, action))
        
        if action == "kill_processes":
            script_path = os.path.join(os.path.dirname(__file__), '../kill_all_and_reset_pegasus.py')
            keyboard.add_hotkey(hotkey, lambda: subprocess.Popen(['python', script_path]))
        else:
            keyboard.add_hotkey(hotkey, lambda action_path=action_path: start_app(action_path))

    print("Listener started. Press Ctrl+C to stop.")
    try:
        # Block forever, waiting for hotkeys
        keyboard.wait()
    except KeyboardInterrupt:
        print("Listener stopped.")

def kill_processes_from_toml(toml_file_path):
    """
    Load the list of processes to kill from a specified TOML file and kill them.
    
    Args:
        toml_file_path (str): Path to the TOML file containing processes to kill.
    """

    print("Loading processes to kill...")
    config = load_toml_config(toml_file_path)
    print("Loaded config:", config)

    processes_to_kill = config.get('processes', {}).get('names', [])
    if not processes_to_kill:
        print("No processes found to kill in the TOML file.")
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
                print(f"Killing process: {proc.info['name']}")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            print(f"Error handling process {proc.info['name']}: {e}")

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
        print(f"Binary not found: {pegasus_binary}")
        return

    try:
        print(f"Starting Pegasus with binary [{pegasus_binary}]...")
        subprocess.Popen(pegasus_binary, shell=True)
        print("Pegasus launched.")
    except Exception as e:
        print(f"Failed to start Pegasus: {e}")

def start_app(executable_path):
    """
    Function to start an application given its executable path.
    """
    try:
        os_type = determine_operating_system()
        print(f"Starting process [{executable_path}] on {os_type}...")

        # Check if the file is a PowerShell script
        if executable_path.endswith('.ps1'):
            if os_type == "Windows":
                # Use PowerShell to execute the script
                subprocess.Popen(['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', executable_path])
            else:
                print("PowerShell scripts are not supported on non-Windows systems.")
        else:
            # Logic to handle different operating systems for other executables
            if os_type == "Windows":
                subprocess.Popen(f'start {executable_path}', shell=True)
            elif os_type == "Darwin":
                subprocess.Popen(['open', executable_path])
            else:
                subprocess.Popen(['xdg-open', executable_path])
        
        print(f"Launched process [{executable_path}].")
    except Exception as e:
        print(f"Failed to start process: {e}")

def kill_process_by_identifier(identifier):
    print("Loading processes to kill...")
    for proc in psutil.process_iter(attrs=["pid", "name", "cmdline"]):
        try:
            cmdline = proc.info["cmdline"]
            if cmdline and any(identifier in arg for arg in cmdline):
                print(f"Found process {proc.pid} with cmdline: {cmdline}")
                # First, kill any children of this process.
                children = proc.children(recursive=True)
                for child in children:
                    print(f"Terminating child process {child.pid} with cmdline: {child.cmdline()}")
                    child.kill()
                # Now kill the process itself.
                print(f"Terminating process {proc.pid} with cmdline: {cmdline}")
                proc.kill()
                proc.wait(timeout=5)
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"Error processing process {proc.pid}: {e}")
            continue


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
        print(f"Unsupported platform: {platform_name}")
        return

    # Iterate over all running processes
    for proc in psutil.process_iter(['name']):
        try:
            # Check if the process name matches any of the Pegasus names
            if proc.info['name'].lower() in (name.lower() for name in process_names):
                print(f"Killing process: {proc.info['name']}")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            print(f"Error handling process {proc.info['name']}: {e}")