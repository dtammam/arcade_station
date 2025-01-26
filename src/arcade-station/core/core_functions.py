import os
import logging
import tomllib  # Use tomllib for Python 3.11 and above
import platform
import subprocess

# function Get-Screenshot
# function Invoke-SetMarqueeFromFile
# function Open-FullscreenImage
# function Send-Keystrokes
# function Set-ForegroundWindow
# function Start-Sound
# function Write-Log... maybe?

def load_config(file_name):
    """
    Load configuration from a specified TOML file.
    """
    config_path = os.path.join(os.path.dirname(__file__), '../../../config', file_name)
    with open(config_path, 'rb') as file:
        return tomllib.load(file)

def open_header(script_name):
    """
    Prepares global variables that will be used for various functions throughout the script.
    Specifically configured for logging locations and exit codes.
    """
    # Determine the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load configuration from default_config.toml
    config = load_config('default_config.toml')
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

def load_installed_games():
    """
    Load installed games configuration from a TOML file.
    """
    return load_config('installed_games.toml')

def get_pegasus_binary(installed_games):
    """
    Returns the path to the appropriate Pegasus binary based on the operating system.
    """
    config = load_config('default_config.toml')
    # Adjust the base path to point directly to the pegasus-fe directory
    pegasus_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../pegasus-fe'))
    
    os_type = platform.system()
    if os_type == "Windows":
        binary_path = os.path.join(pegasus_base_path, installed_games['pegasus']['windows_binary'])
    elif os_type == "Darwin":
        binary_path = os.path.join(pegasus_base_path, installed_games['pegasus']['mac_binary'])
    else:
        binary_path = os.path.join(pegasus_base_path, installed_games['pegasus']['linux_binary'])
    
    print(f"Constructed binary path: {binary_path}")  # Debug print
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