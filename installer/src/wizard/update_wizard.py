"""
Update Wizard for Arcade Station Installer.

This module provides the wizard for updating an existing installation of Arcade Station,
allowing users to modify their configuration.
"""

import os
import sys
import logging
from pathlib import Path

# Import from parent directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from wizard.base_wizard import BaseWizardApp
from core.core_functions import convert_path_for_platform, logger

# Import required configurators
from configurators.toml_manager import TomlConfigManager
from configurators.pegasus_manager import PegasusMetadataManager

# Import wizard pages
# Will be implemented in future

class UpdateWizard(BaseWizardApp):
    """
    Wizard for updating an existing installation of Arcade Station.
    
    This wizard allows users to modify their configuration and
    add/remove games from an existing Arcade Station installation.
    """
    
    def __init__(self, install_path, theme="dark"):
        """
        Initialize the update wizard.
        
        Args:
            install_path (str): Path to the existing installation.
            theme (str): UI theme ("dark" or "light").
        """
        super().__init__(title="Arcade Station - Configuration Update", theme=theme)
        
        # Store installation path
        self.install_path = convert_path_for_platform(install_path)
        
        # Initialize configurators
        self.setup_configurators()
        
        # Load existing configuration
        self.load_configuration()
        
        # Register wizard pages
        self.register_wizard_pages()
    
    def setup_configurators(self):
        """
        Set up configuration managers with the correct paths.
        """
        # Create config directory path
        config_dir = os.path.join(self.install_path, 'config')
        
        # Create metafiles directory path
        metafiles_dir = os.path.join(self.install_path, 'src', 'pegasus-fe', 'config', 'metafiles')
        
        # Initialize configurators
        self.toml_manager = TomlConfigManager(config_dir)
        self.pegasus_manager = PegasusMetadataManager(metafiles_dir)
    
    def load_configuration(self):
        """
        Load existing configuration from the installation.
        """
        # Initialize configuration data
        self.config_data = {
            'install_path': self.install_path,
            
            # Dynamic marquee
            'dynamic_marquee_enabled': False,
            'dynamic_marquee_display': 0,
            'dynamic_marquee_default_image': '',
            
            # ITGMania
            'itgmania_enabled': False,
            'itgmania_path': '',
            'itgmania_dynamic_marquee': False,
            
            # Control configuration
            'key_bindings': {},
            
            # Utility features
            'lights_enabled': False,
            'vpn_enabled': False,
            'streaming_enabled': False,
            'logging_enabled': True,
            'logging_directory': ''
        }
        
        try:
            # Load display configuration
            display_config = self.toml_manager.read_config('display_config')
            if display_config and 'dynamic_marquee' in display_config:
                self.config_data['dynamic_marquee_enabled'] = display_config['dynamic_marquee'].get('enabled', False)
                self.config_data['dynamic_marquee_display'] = display_config['dynamic_marquee'].get('display_number', 0)
                self.config_data['dynamic_marquee_default_image'] = display_config['dynamic_marquee'].get('default_image', '')
            
            if display_config and 'itgmania_display' in display_config:
                self.config_data['itgmania_dynamic_marquee'] = display_config['itgmania_display'].get('enabled', False)
            
            # Load installed games
            games_config = self.toml_manager.read_config('installed_games')
            if games_config:
                # Check for ITGMania
                if 'binary_games' in games_config and 'itgmania' in games_config['binary_games']:
                    self.config_data['itgmania_enabled'] = True
                    self.config_data['itgmania_path'] = games_config['binary_games']['itgmania'].get('path', '')
            
            # Load key bindings
            key_config = self.toml_manager.read_config('key_listener')
            if key_config and 'shortcuts' in key_config:
                self.config_data['key_bindings'] = key_config['shortcuts']
            
            # Load utility configuration
            utility_config = self.toml_manager.read_config('utility_config')
            if utility_config:
                if 'lights' in utility_config:
                    self.config_data['lights_enabled'] = utility_config['lights'].get('enabled', False)
                
                if 'vpn' in utility_config:
                    self.config_data['vpn_enabled'] = utility_config['vpn'].get('enabled', False)
                
                if 'streaming' in utility_config:
                    self.config_data['streaming_enabled'] = utility_config['streaming'].get('webcam_management_enabled', False)
            
            # Load logging configuration
            default_config = self.toml_manager.read_config('default_config')
            if default_config and 'logging' in default_config:
                self.config_data['logging_enabled'] = True
                self.config_data['logging_directory'] = default_config['logging'].get('logdirectory', os.path.join(self.install_path, 'logs'))
            
            logger.info("Successfully loaded existing configuration")
            
        except Exception as e:
            logger.error(f"Error loading existing configuration: {str(e)}")
    
    def register_wizard_pages(self):
        """
        Register all pages for the wizard.
        """
        # TODO: Implement update wizard pages
        # For now, just add a placeholder page that shows a "not implemented" message
        
        # Import placeholder page
        from wizard.pages.welcome_page import WelcomePage
        
        # Register welcome page for now
        self.register_page("welcome", WelcomePage)
    
    def apply_changes(self):
        """
        Apply configuration changes to the existing installation.
        
        Returns:
            tuple: (success, message) - Success status and message.
        """
        # TODO: Implement applying changes to existing installation
        return True, "Update not implemented yet"
    
    def exit(self):
        """
        Close the wizard and apply changes if finished.
        """
        # Check if we're on the last page
        if self.current_page == self.page_order[-1]:
            # Apply changes
            success, message = self.apply_changes()
            
            if success:
                # Show success message
                self.show_message(
                    "Update Complete",
                    "Arcade Station configuration has been updated successfully!",
                    "info"
                )
            else:
                # Show error message
                self.show_message(
                    "Update Failed",
                    f"An error occurred during the update: {message}",
                    "error"
                )
        
        # Close the wizard
        super().exit() 