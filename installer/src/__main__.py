#!/usr/bin/env python3
"""
Arcade Station Installer - Main Entry Point

This is the main entry point for the Arcade Station installer.
It detects if Arcade Station is already installed and launches
the appropriate wizard based on the installation status.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Check Python version
REQUIRED_PYTHON_VERSION = (3, 12, 9)
if sys.version_info[:3] < REQUIRED_PYTHON_VERSION:
    print(f"Error: Python {REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]}.{REQUIRED_PYTHON_VERSION[2]} or higher is required")
    print(f"Current Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    sys.exit(1)

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("ArcadeStationInstaller")

# Add the installer directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import core functions
from core.core_functions import is_installed, is_admin, setup_logging

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Arcade Station Installer")
    
    parser.add_argument(
        "--reset", 
        action="store_true", 
        help="Reset configuration and reinstall"
    )
    
    parser.add_argument(
        "--install-path", 
        type=str, 
        help="Custom installation path"
    )
    
    parser.add_argument(
        "--log-dir", 
        type=str, 
        help="Directory for log files"
    )
    
    parser.add_argument(
        "--theme", 
        type=str, 
        choices=["dark", "light"], 
        default="dark", 
        help="UI theme (dark/light)"
    )
    
    parser.add_argument(
        "--skip-admin-check", 
        action="store_true", 
        help="Skip administrator privileges check"
    )
    
    return parser.parse_args()

def check_prerequisites():
    """
    Check if all prerequisites are met.
    
    Returns:
        tuple: (bool, str) - Success status and message.
    """
    # Check Python version
    current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    required_version = f"{REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]}.{REQUIRED_PYTHON_VERSION[2]}"
    
    if sys.version_info[:3] != REQUIRED_PYTHON_VERSION:
        logger.warning(f"Using Python {current_version}, but {required_version} is recommended")
    else:
        logger.info(f"Using Python {current_version}")
    
    # Check for CustomTkinter
    try:
        import customtkinter
        logger.info("CustomTkinter is installed")
    except ImportError:
        logger.warning("CustomTkinter is not installed. The installer will use standard Tkinter with basic styling.")
    
    # Check for tomlkit (required for writing TOML files)
    try:
        import tomlkit
        logger.info("tomlkit is installed")
    except ImportError:
        logger.error("tomlkit is not installed. Please install it with 'pip install tomlkit'.")
        return False, "Missing required package: tomlkit. Please install it with 'pip install tomlkit'."
    
    # Check for administrator privileges on Windows for features that need it
    if sys.platform == 'win32' and not is_admin():
        logger.warning("Not running with administrator privileges. Some features may not work.")
    
    return True, "All prerequisites met"

def main():
    """
    Main entry point for the installer.
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up logging
    if args.log_dir:
        log_file = setup_logging(args.log_dir)
        logger.info(f"Logging to {log_file}")
    
    # Check prerequisites
    prereqs_ok, prereqs_msg = check_prerequisites()
    if not prereqs_ok:
        logger.error(f"Prerequisites check failed: {prereqs_msg}")
        print(f"Error: {prereqs_msg}")
        sys.exit(1)
    
    # Check if we need to enforce admin privileges
    if sys.platform == 'win32' and not args.skip_admin_check and not is_admin():
        # Only require admin for Windows if not explicitly skipped
        logger.warning("Administrator privileges are required for full functionality.")
        print("This installer requires administrator privileges for full functionality.")
        print("Please run the installer as administrator.")
        
        # Ask user if they want to continue anyway
        response = input("Continue without administrator privileges? (y/N): ").strip().lower()
        if response != 'y':
            logger.info("User chose to exit due to lack of administrator privileges")
            sys.exit(0)
    
    # Check if Arcade Station is already installed
    is_already_installed, install_path = is_installed(args.install_path)
    
    # Override with reset flag if specified
    if args.reset:
        is_already_installed = False
        logger.info("Reset flag specified, treating as new installation")
    
    # Import the appropriate wizard based on installation status
    if is_already_installed:
        logger.info(f"Arcade Station is already installed at {install_path}")
        print(f"Arcade Station is already installed at {install_path}")
        
        try:
            from wizard.update_wizard import UpdateWizard
            
            # Create and start the update wizard
            wizard = UpdateWizard(install_path=install_path, theme=args.theme)
            wizard.start()
            
        except Exception as e:
            logger.exception("Error starting update wizard")
            print(f"Error: {str(e)}")
            sys.exit(1)
    else:
        logger.info("Arcade Station is not installed or reset was requested")
        
        try:
            from wizard.initial_wizard import InitialWizard
            
            # Create and start the initial setup wizard
            wizard = InitialWizard(
                install_path=args.install_path, 
                theme=args.theme
            )
            wizard.start()
            
        except Exception as e:
            logger.exception("Error starting initial wizard")
            print(f"Error: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Installation cancelled by user")
        print("\nInstallation cancelled.")
        sys.exit(0)
    except Exception as e:
        logger.exception("Unhandled exception")
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(1) 