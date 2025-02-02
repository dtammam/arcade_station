import os
import logging
import tomllib
import platform
import subprocess
import psutil
import keyboard

# function Get-Screenshot
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
    return load_toml_config('installed_games.toml')

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
