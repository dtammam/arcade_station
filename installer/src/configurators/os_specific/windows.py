"""
Windows-specific Configuration Module for Arcade Station Installer.

This module provides Windows-specific functionality for the Arcade Station installer,
including registry operations, auto-login setup, and shell replacement.
"""

import os
import sys
import logging
import subprocess
import ctypes
import winreg

# Import core functions
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from core.core_functions import run_command, logger

def is_admin():
    """
    Check if the current process has administrator privileges.
    
    Returns:
        bool: True if running with admin privileges, False otherwise.
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def setup_auto_login(username, password=None, domain=None):
    """
    Configure Windows to automatically log in with the specified user.
    
    Args:
        username (str): Username to automatically log in with.
        password (str, optional): Password for the user account. If None, will be prompted.
        domain (str, optional): Domain for the user account. If None, uses local machine.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    if not is_admin():
        logger.error("Administrator privileges are required to set up auto-login")
        return False
    
    try:
        # Set up required registry values for auto-login
        winlogon_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon",
            0, 
            winreg.KEY_SET_VALUE | winreg.KEY_WRITE
        )
        
        # Set AutoAdminLogon to 1
        winreg.SetValueEx(winlogon_key, "AutoAdminLogon", 0, winreg.REG_SZ, "1")
        
        # Set DefaultUserName
        winreg.SetValueEx(winlogon_key, "DefaultUserName", 0, winreg.REG_SZ, username)
        
        # Set DefaultDomainName if provided
        if domain:
            winreg.SetValueEx(winlogon_key, "DefaultDomainName", 0, winreg.REG_SZ, domain)
        
        # Set DefaultPassword if provided
        if password:
            winreg.SetValueEx(winlogon_key, "DefaultPassword", 0, winreg.REG_SZ, password)
        
        winreg.CloseKey(winlogon_key)
        
        logger.info("Auto-login configured successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error setting up auto-login: {str(e)}")
        return False

def setup_shell_replacement(shell_path):
    """
    Configure Windows to use a custom shell instead of Explorer.
    
    Args:
        shell_path (str): Path to the custom shell executable or script.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    if not is_admin():
        logger.error("Administrator privileges are required to set up shell replacement")
        return False
    
    try:
        # Convert shell_path to absolute path if it's not already
        shell_path = os.path.abspath(shell_path)
        
        # Ensure the shell path exists
        if not os.path.exists(shell_path):
            logger.error(f"Shell path does not exist: {shell_path}")
            return False
        
        # Set up the registry key for shell replacement
        winlogon_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon",
            0, 
            winreg.KEY_SET_VALUE | winreg.KEY_WRITE
        )
        
        # Set the Shell value
        winreg.SetValueEx(winlogon_key, "Shell", 0, winreg.REG_SZ, shell_path)
        
        winreg.CloseKey(winlogon_key)
        
        logger.info(f"Shell replacement configured successfully: {shell_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error setting up shell replacement: {str(e)}")
        return False

def restore_default_shell():
    """
    Restore the default Windows shell (explorer.exe).
    
    Returns:
        bool: True if successful, False otherwise.
    """
    if not is_admin():
        logger.error("Administrator privileges are required to restore the default shell")
        return False
    
    try:
        # Set up the registry key
        winlogon_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon",
            0, 
            winreg.KEY_SET_VALUE | winreg.KEY_WRITE
        )
        
        # Set the Shell value back to explorer.exe
        winreg.SetValueEx(winlogon_key, "Shell", 0, winreg.REG_SZ, "explorer.exe")
        
        winreg.CloseKey(winlogon_key)
        
        logger.info("Default shell (explorer.exe) restored successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error restoring default shell: {str(e)}")
        return False

def setup_startup_script(script_path, username=None):
    """
    Configure a script to run at Windows startup.
    
    Args:
        script_path (str): Path to the script to run at startup.
        username (str, optional): Username for which to set up the startup. 
                                  If None, uses current user.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Convert script_path to absolute path if it's not already
        script_path = os.path.abspath(script_path)
        
        # Ensure the script path exists
        if not os.path.exists(script_path):
            logger.error(f"Script path does not exist: {script_path}")
            return False
        
        # Determine the startup folder
        if username:
            # Get the user's profile directory
            success, output = run_command(
                ['powershell', '-Command', f'(Get-CimInstance -ClassName Win32_UserProfile | Where-Object {{ $_.LocalPath -like "*{username}*" }}).LocalPath'], 
                shell=False
            )
            
            if not success or not output:
                logger.error(f"Could not find profile directory for user: {username}")
                return False
                
            startup_folder = os.path.join(output.strip(), r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup")
        else:
            # Use current user's startup folder
            startup_folder = os.path.join(
                os.environ.get('APPDATA', ''), 
                r"Microsoft\Windows\Start Menu\Programs\Startup"
            )
        
        # Ensure the startup folder exists
        os.makedirs(startup_folder, exist_ok=True)
        
        # Create a shortcut or batch file to run the script
        shortcut_path = os.path.join(startup_folder, "ArcadeStationStartup.bat")
        
        with open(shortcut_path, 'w') as f:
            f.write(f'@echo off\nstart "" "{script_path}"\n')
        
        logger.info(f"Startup script set up successfully: {shortcut_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error setting up startup script: {str(e)}")
        return False

def setup_kiosk_mode(install_path, username=None, password=None, domain=None):
    """
    Set up Windows kiosk mode for Arcade Station.
    
    This combines auto-login and shell replacement to create a dedicated
    Arcade Station experience on Windows.
    
    Args:
        install_path (str): Installation path for Arcade Station.
        username (str, optional): Username to automatically log in with. If None, uses current user.
        password (str, optional): Password for the user account.
        domain (str, optional): Domain for the user account. If None, uses local machine.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    if not is_admin():
        logger.error("Administrator privileges are required to set up kiosk mode")
        return False
    
    try:
        # Use current user if username is not provided
        if not username:
            username = os.environ.get('USERNAME', '')
        
        # Set up auto-login
        auto_login_success = setup_auto_login(username, password, domain)
        if not auto_login_success:
            logger.error("Failed to set up auto-login")
            return False
        
        # Path to the Arcade Station startup batch file
        startup_bat = os.path.join(install_path, "arcade_station_start_windows.bat")
        
        # Set up shell replacement
        shell_replacement_success = setup_shell_replacement(startup_bat)
        if not shell_replacement_success:
            logger.error("Failed to set up shell replacement")
            # Attempt to roll back auto-login
            try:
                winlogon_key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon",
                    0, 
                    winreg.KEY_SET_VALUE | winreg.KEY_WRITE
                )
                winreg.SetValueEx(winlogon_key, "AutoAdminLogon", 0, winreg.REG_SZ, "0")
                winreg.CloseKey(winlogon_key)
            except:
                pass
            return False
        
        logger.info("Kiosk mode set up successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error setting up kiosk mode: {str(e)}")
        return False

def disable_kiosk_mode():
    """
    Disable kiosk mode by restoring default Windows settings.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    if not is_admin():
        logger.error("Administrator privileges are required to disable kiosk mode")
        return False
    
    try:
        # Restore default shell
        shell_restore_success = restore_default_shell()
        if not shell_restore_success:
            logger.error("Failed to restore default shell")
            return False
        
        # Disable auto-login
        try:
            winlogon_key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon",
                0, 
                winreg.KEY_SET_VALUE | winreg.KEY_WRITE
            )
            winreg.SetValueEx(winlogon_key, "AutoAdminLogon", 0, winreg.REG_SZ, "0")
            winreg.CloseKey(winlogon_key)
        except Exception as e:
            logger.error(f"Error disabling auto-login: {str(e)}")
            return False
        
        logger.info("Kiosk mode disabled successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error disabling kiosk mode: {str(e)}")
        return False 