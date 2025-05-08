"""
Arcade Station Installer Package
"""
import platform
import os

__version__ = "0.1.0"

# Detect the current platform
CURRENT_OS = platform.system().lower()
IS_WINDOWS = CURRENT_OS == "windows"
IS_LINUX = CURRENT_OS == "linux"
IS_MAC = CURRENT_OS == "darwin"

# Common paths
INSTALLER_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(os.path.dirname(INSTALLER_DIR), "resources")

def get_platform_name():
    """Get a human-readable platform name for display purposes."""
    if IS_WINDOWS:
        return "Windows"
    elif IS_LINUX:
        return "Linux"
    elif IS_MAC:
        return "macOS"
    else:
        return "Unknown" 