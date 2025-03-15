"""
TOML Configuration Manager for Arcade Station Installer.

This module provides a comprehensive interface for handling TOML configuration
files used by Arcade Station. It manages reading, writing, and updating all
configuration files with appropriate error handling and validation.
"""

import os
import copy
import sys
import logging
from pathlib import Path

# Since tomllib is read-only, we use tomlkit for writing
import tomllib
import tomlkit

# Import core functions
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.core_functions import convert_path_for_platform

logger = logging.getLogger("ArcadeStationInstaller")

class TomlConfigManager:
    """
    Manages all TOML configuration files for the Arcade Station installer.
    
    This class provides an interface for reading, writing, and modifying all
    configuration files used by Arcade Station.
    """
    
    def __init__(self, config_dir):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir (str): Path to the directory containing configuration files.
        """
        self.config_dir = config_dir
        # Ensure the config directory exists
        os.makedirs(config_dir, exist_ok=True)
        
        # Dictionary to cache configurations
        self.config_cache = {}
        
    def get_config_path(self, config_name):
        """
        Get the full path to a configuration file.
        
        Args:
            config_name (str): Name of the configuration file.
            
        Returns:
            str: Full path to the configuration file.
        """
        # Add .toml extension if not provided
        if not config_name.endswith('.toml'):
            config_name += '.toml'
        
        return os.path.join(self.config_dir, config_name)
    
    def read_config(self, config_name, force_reload=False):
        """
        Read and parse a TOML configuration file.
        
        Args:
            config_name (str): Name of the configuration file.
            force_reload (bool): Whether to force reload from disk even if cached.
            
        Returns:
            dict: Parsed TOML content as a dictionary.
        """
        if not config_name.endswith('.toml'):
            config_name += '.toml'
            
        # Check if config is cached and force_reload is not set
        if not force_reload and config_name in self.config_cache:
            return copy.deepcopy(self.config_cache[config_name])
            
        config_path = self.get_config_path(config_name)
        
        try:
            # Read and parse TOML
            if os.path.exists(config_path):
                with open(config_path, 'rb') as f:
                    config_data = tomllib.load(f)
                
                # Cache the config
                self.config_cache[config_name] = copy.deepcopy(config_data)
                return config_data
            else:
                logger.warning(f"Configuration file not found: {config_path}")
                return {}
        except Exception as e:
            logger.error(f"Error reading TOML file {config_path}: {str(e)}")
            return {}
    
    def write_config(self, config_name, config_data, merge=False):
        """
        Write a dictionary to a TOML configuration file.
        
        Args:
            config_name (str): Name of the configuration file.
            config_data (dict): Dictionary to convert to TOML and write.
            merge (bool): Whether to merge with existing config or overwrite.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if not config_name.endswith('.toml'):
            config_name += '.toml'
            
        config_path = self.get_config_path(config_name)
        
        try:
            # If merging and file exists, read existing config first
            if merge and os.path.exists(config_path):
                existing_data = self.read_config(config_name, force_reload=True)
                
                # Deep merge the dictionaries
                merged_data = self._deep_merge(existing_data, config_data)
                final_data = merged_data
            else:
                final_data = config_data
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # Use tomlkit to preserve formatting
            doc = tomlkit.document()
            
            for section_name, section_data in final_data.items():
                table = tomlkit.table()
                
                # Add items to the table
                if isinstance(section_data, dict):
                    for key, value in section_data.items():
                        table.add(key, value)
                    
                    # Add the table to the document
                    doc.add(section_name, table)
                else:
                    # If section is not a dict, add it directly
                    doc.add(section_name, section_data)
            
            # Write the document to file
            with open(config_path, 'w') as f:
                f.write(tomlkit.dumps(doc))
            
            # Update cache
            self.config_cache[config_name] = copy.deepcopy(final_data)
            
            logger.info(f"Successfully wrote configuration to {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing TOML file {config_path}: {str(e)}")
            return False
    
    def update_config(self, config_name, section, key, value):
        """
        Update a specific key in a configuration file.
        
        Args:
            config_name (str): Name of the configuration file.
            section (str): Section of the configuration to update.
            key (str): Key to update.
            value: New value for the key.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        # Read current config
        config_data = self.read_config(config_name)
        
        # Create section if it doesn't exist
        if section not in config_data:
            config_data[section] = {}
        
        # Update the key
        config_data[section][key] = value
        
        # Write updated config back
        return self.write_config(config_name, config_data)
    
    def get_value(self, config_name, section, key, default=None):
        """
        Get a specific value from a configuration file.
        
        Args:
            config_name (str): Name of the configuration file.
            section (str): Section of the configuration to read from.
            key (str): Key to read.
            default: Default value to return if key or section not found.
            
        Returns:
            The value from the configuration, or default if not found.
        """
        config_data = self.read_config(config_name)
        
        # Check if section exists
        if section in config_data:
            # Check if key exists
            if key in config_data[section]:
                return config_data[section][key]
        
        return default
    
    def create_default_configs(self, install_path):
        """
        Create default configuration files for a fresh installation.
        
        Args:
            install_path (str): Installation path for Arcade Station.
            
        Returns:
            bool: True if all configurations were created successfully, False otherwise.
        """
        success = True
        install_path = convert_path_for_platform(install_path)
        
        # Create default_config.toml
        default_config = {
            'logging': {
                'logdirectory': os.path.join(install_path, 'logs')
            }
        }
        if not self.write_config('default_config', default_config):
            success = False
        
        # Create display_config.toml
        display_config = {
            'dynamic_marquee': {
                'enabled': False,
                'display_number': 0,
                'default_image': os.path.join(install_path, 'assets', 'images', 'arcade_station_marquee.png')
            },
            'itgmania_display': {
                'enabled': False,
                'log_file': os.path.join(install_path, 'logs', 'itgmania.log')
            }
        }
        if not self.write_config('display_config', display_config):
            success = False
        
        # Create empty installed_games.toml
        installed_games = {
            'binary_games': {},
            'mame_games': {}
        }
        if not self.write_config('installed_games', installed_games):
            success = False
        
        # Create key_listener.toml
        key_listener = {
            'shortcuts': {
                'kill_all_and_reset_pegasus': 'ctrl+alt+r',
                'take_screenshot': 'ctrl+alt+s',
                'start_streaming': 'ctrl+alt+b'
            }
        }
        if not self.write_config('key_listener', key_listener):
            success = False
        
        # Create processes_to_kill.toml
        processes_to_kill = {
            'processes': [
                'mame64.exe',
                'ITGmania.exe',
                'stepmania.exe',
                'obs64.exe',
                'LogiCapture.exe'
            ]
        }
        if not self.write_config('processes_to_kill', processes_to_kill):
            success = False
        
        # Create mame_config.toml
        mame_config = {
            'mame': {
                'executable': '',
                'inipath': ''
            }
        }
        if not self.write_config('mame_config', mame_config):
            success = False
        
        # Create pegasus_binaries.toml
        pegasus_binaries = {
            'pegasus': {
                'executable': ''
            }
        }
        if not self.write_config('pegasus_binaries', pegasus_binaries):
            success = False
        
        # Create screenshot_config.toml
        screenshot_config = {
            'screenshot': {
                'monitor': 0,
                'save_directory': os.path.join(install_path, 'screenshots'),
                'sound': ''
            },
            'icloud': {
                'enabled': False,
                'restart_services': False
            }
        }
        if not self.write_config('screenshot_config', screenshot_config):
            success = False
        
        # Create utility_config.toml
        utility_config = {
            'lights': {
                'enabled': False,
                'light_reset_executable_path': '',
                'light_mame_executable_path': ''
            },
            'streaming': {
                'webcam_management_enabled': False,
                'webcam_management_executable': '',
                'obs_executable': '',
                'obs_arguments': '--startstreaming --disable-shutdown-check'
            },
            'vpn': {
                'enabled': False,
                'vpn_application_directory': '',
                'vpn_application': '',
                'vpn_process': '',
                'vpn_config_profile': '',
                'seconds_to_wait': 10
            },
            'osd': {
                'enabled': False,
                'sound_osd_executable': ''
            }
        }
        if not self.write_config('utility_config', utility_config):
            success = False
        
        return success
    
    def _deep_merge(self, dict1, dict2):
        """
        Deep merge two dictionaries.
        
        Args:
            dict1 (dict): First dictionary.
            dict2 (dict): Second dictionary to merge into the first.
            
        Returns:
            dict: Merged dictionary.
        """
        result = copy.deepcopy(dict1)
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = copy.deepcopy(value)
                
        return result 