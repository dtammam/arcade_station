"""
Core Functions Module for Arcade Station Installer.

This module contains essential utilities and functions used throughout the Arcade Station
Installer application. It handles configuration loading, platform detection,
file operations, and common operations needed for the installation process.

The functions in this module are designed to be platform-agnostic where possible,
with platform-specific implementations when necessary.
"""

import os
import sys
import logging
import platform
import tomllib
import subprocess
import shutil
from datetime import datetime

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("ArcadeStationInstaller")

def setup_logging(log_dir=None):
    """
    Set up logging for the installer.
    
    Args:
        log_dir (str, optional): Directory to store log files. If None, logs only to console.
        
    Returns:
        str: Path to the log file if created, None otherwise.
    """
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"arcade_station_installer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s'))
        logger.addHandler(file_handler)
        
        return log_file
    return None

def determine_operating_system():
    """
    Detect the current operating system.
    
    Returns:
        str: The detected operating system - 'Windows', 'Linux', 'Darwin' (macOS),
            or 'Unknown' if the platform cannot be determined.
    """
    return platform.system()

def is_admin():
    """
    Check if the current process has administrator/root privileges.
    
    Returns:
        bool: True if running with admin/root privileges, False otherwise.
    """
    try:
        if determine_operating_system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            # Unix-based systems - root has UID 0
            return os.geteuid() == 0
    except:
        # If there's an error, assume not admin
        return False

def read_toml_file(file_path):
    """
    Read and parse a TOML file.
    
    Args:
        file_path (str): Path to the TOML file.
        
    Returns:
        dict: Parsed TOML content as a dictionary, or empty dict if file not found or invalid.
    """
    try:
        with open(file_path, 'rb') as f:
            return tomllib.load(f)
    except FileNotFoundError:
        logger.warning(f"TOML file not found: {file_path}")
        return {}
    except Exception as e:
        logger.error(f"Error reading TOML file {file_path}: {str(e)}")
        return {}

def write_toml_file(file_path, data):
    """
    Write a dictionary to a TOML file.
    
    Args:
        file_path (str): Path where to write the TOML file.
        data (dict): Dictionary to convert to TOML and write.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Since tomllib doesn't support writing, we use tomlkit
        import tomlkit
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write(tomlkit.dumps(data))
        return True
    except Exception as e:
        logger.error(f"Error writing TOML file {file_path}: {str(e)}")
        return False

def convert_path_for_platform(path):
    """
    Convert file paths to be compatible with the current operating system.
    
    Args:
        path (str): The file path to convert.
        
    Returns:
        str: The converted path appropriate for the current platform.
    """
    if not path:
        return path
        
    # Convert slashes based on current OS
    os_type = determine_operating_system()
    if os_type == "Windows":
        # Replace forward slashes with backslashes for Windows
        return path.replace('/', '\\')
    else:
        # Replace backslashes with forward slashes for Unix-like systems
        return path.replace('\\', '/')

def copy_directory(src, dst, ignore_patterns=None):
    """
    Copy a directory and its contents.
    
    Args:
        src (str): Source directory path.
        dst (str): Destination directory path.
        ignore_patterns (list, optional): List of file patterns to ignore.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        if ignore_patterns:
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*ignore_patterns), dirs_exist_ok=True)
        else:
            shutil.copytree(src, dst, dirs_exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error copying directory {src} to {dst}: {str(e)}")
        return False

def is_installed(install_path=None):
    """
    Check if Arcade Station is already installed.
    
    Args:
        install_path (str, optional): Path to check for installation.
        
    Returns:
        tuple: (is_installed, install_path) - Boolean indicating if installed and the install path.
    """
    # Look for specific config files or markers
    if install_path is None:
        # Check default locations based on OS
        if sys.platform == 'win32':
            possible_paths = [
                os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'arcade_station'),
                os.path.join(os.environ.get('LOCALAPPDATA', 'C:\\Users\\' + os.getlogin() + '\\AppData\\Local'), 'arcade_station')
            ]
        elif sys.platform == 'darwin':  # macOS
            possible_paths = [
                '/Applications/arcade_station',
                os.path.expanduser('~/Applications/arcade_station')
            ]
        else:  # Linux
            possible_paths = [
                '/opt/arcade_station',
                os.path.expanduser('~/.local/share/arcade_station')
            ]
        
        for path in possible_paths:
            if os.path.exists(os.path.join(path, 'config/default_config.toml')):
                return True, path
        return False, None
    else:
        return os.path.exists(os.path.join(install_path, 'config/default_config.toml')), install_path

def get_default_install_path():
    """
    Get the default installation path for the current platform.
    
    Returns:
        str: Default installation path.
    """
    if sys.platform == 'win32':
        return os.path.join(os.environ.get('LOCALAPPDATA', 'C:\\Users\\' + os.getlogin() + '\\AppData\\Local'), 'arcade_station')
    elif sys.platform == 'darwin':  # macOS
        return os.path.expanduser('~/Applications/arcade_station')
    else:  # Linux
        return os.path.expanduser('~/.local/share/arcade_station')

def run_command(command, shell=False):
    """
    Run a system command and return the result.
    
    Args:
        command (str or list): Command to run as string or list of arguments.
        shell (bool): Whether to run the command in a shell.
        
    Returns:
        tuple: (success, output) - Boolean indicating success and command output.
    """
    try:
        result = subprocess.run(
            command, 
            shell=shell, 
            capture_output=True, 
            text=True, 
            check=False
        )
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        logger.error(f"Error running command {command}: {str(e)}")
        return False, str(e)

def detect_monitors():
    """
    Detect available monitors on the system.
    
    Returns:
        list: List of monitor information dictionaries.
    """
    monitors = []
    
    try:
        # Platform-specific monitor detection
        if sys.platform == 'win32':
            # Windows - use pywin32 if available
            try:
                import win32api
                monitor_info = []
                for i, monitor in enumerate(win32api.EnumDisplayMonitors()):
                    info = win32api.GetMonitorInfo(monitor[0])
                    width = info['Monitor'][2] - info['Monitor'][0]
                    height = info['Monitor'][3] - info['Monitor'][1]
                    is_primary = (info['Flags'] == 1)
                    monitors.append({
                        'id': i,
                        'name': f"Monitor {i+1}" + (" (Primary)" if is_primary else ""),
                        'width': width,
                        'height': height,
                        'is_primary': is_primary
                    })
            except ImportError:
                # Fallback if pywin32 is not available
                import ctypes
                user32 = ctypes.windll.user32
                monitors_count = user32.GetSystemMetrics(80)  # SM_CMONITORS
                for i in range(monitors_count):
                    monitors.append({
                        'id': i,
                        'name': f"Monitor {i+1}",
                        'width': user32.GetSystemMetrics(0),  # SM_CXSCREEN
                        'height': user32.GetSystemMetrics(1)  # SM_CYSCREEN
                    })
        elif sys.platform == 'darwin':  # macOS
            # Use objective-c bridge if available
            try:
                from AppKit import NSScreen
                for i, screen in enumerate(NSScreen.screens()):
                    frame = screen.frame()
                    monitors.append({
                        'id': i,
                        'name': f"Display {i+1}",
                        'width': int(frame.size.width),
                        'height': int(frame.size.height),
                        'is_primary': (i == 0)  # Assume first screen is primary
                    })
            except ImportError:
                # Fallback to using system profiler
                success, output = run_command(['system_profiler', 'SPDisplaysDataType'], shell=False)
                if success:
                    monitors.append({'id': 0, 'name': 'Primary Display', 'is_primary': True})
        else:  # Linux
            try:
                # Try using xrandr
                success, output = run_command(['xrandr', '--query'], shell=False)
                if success:
                    import re
                    connected_displays = re.findall(r'(\S+) connected (\d+)x(\d+)', output)
                    for i, display in enumerate(connected_displays):
                        name, width, height = display
                        monitors.append({
                            'id': i,
                            'name': name,
                            'width': int(width),
                            'height': int(height),
                            'is_primary': 'primary' in output.split(name)[1].split('\n')[0]
                        })
            except Exception:
                # Fallback for Linux
                monitors.append({'id': 0, 'name': 'Primary Display', 'is_primary': True})
    
    except Exception as e:
        logger.error(f"Error detecting monitors: {str(e)}")
    
    # If all detection methods failed, return at least one monitor
    if not monitors:
        monitors.append({'id': 0, 'name': 'Primary Display', 'is_primary': True})
    
    return monitors 