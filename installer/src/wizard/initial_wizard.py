"""
Initial Setup Wizard for Arcade Station Installer.

This module provides the wizard for first-time installation of Arcade Station,
guiding users through the complete setup process.
"""

import os
import sys
import logging
import shutil
from pathlib import Path

# Import from parent directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from wizard.base_wizard import BaseWizardApp
from core.core_functions import get_default_install_path, convert_path_for_platform, logger

# Import required configurators
from configurators.toml_manager import TomlConfigManager
from configurators.pegasus_manager import PegasusMetadataManager

# Import wizard pages
from wizard.pages.welcome_page import WelcomePage
# Import other pages as they're created
# from wizard.pages.installation_path_page import InstallationPathPage
# from wizard.pages.kiosk_mode_page import KioskModePage
# etc.

class InitialWizard(BaseWizardApp):
    """
    Wizard for first-time installation of Arcade Station.
    
    This wizard guides users through the complete setup process for a
    new installation of Arcade Station.
    """
    
    def __init__(self, install_path=None, theme="dark"):
        """
        Initialize the initial setup wizard.
        
        Args:
            install_path (str, optional): Custom installation path. If None, uses default.
            theme (str): UI theme ("dark" or "light").
        """
        super().__init__(title="Arcade Station - Initial Setup", theme=theme)
        
        # Set initial installation path
        if install_path:
            self.install_path = install_path
        else:
            self.install_path = get_default_install_path()
        
        # Initialize configurators
        self.toml_manager = None
        self.pegasus_manager = None
        
        # Initialize installation variables
        self.setup_installation_variables()
        
        # Register wizard pages
        self.register_wizard_pages()
    
    def setup_installation_variables(self):
        """
        Set up variables for the installation process.
        """
        # Basic installation info
        self.config_data = {
            'install_path': self.install_path,
            'kiosk_mode': False,
            'kiosk_mode_username': '',
            'kiosk_mode_password': '',
            'create_shortcut': True,
            
            # Dynamic marquee
            'dynamic_marquee_enabled': False,
            'dynamic_marquee_display': 0,
            'dynamic_marquee_default_image': '',
            
            # ITGMania
            'itgmania_enabled': False,
            'itgmania_path': '',
            'itgmania_dynamic_marquee': False,
            
            # Games
            'binary_games': {},
            'mame_games': {},
            
            # Control configuration
            'key_bindings': {
                'kill_all_and_reset_pegasus': 'ctrl+alt+r',
                'take_screenshot': 'ctrl+alt+s',
                'start_streaming': 'ctrl+alt+b'
            },
            
            # Utility features
            'lights_enabled': False,
            'vpn_enabled': False,
            'streaming_enabled': False,
            'logging_enabled': True,
            'logging_directory': ''
        }
    
    def register_wizard_pages(self):
        """
        Register all pages for the wizard.
        """
        # Welcome page
        self.register_page("welcome", WelcomePage)
        
        # TODO: Register other pages as they're created
        # self.register_page("installation_path", InstallationPathPage)
        # self.register_page("kiosk_mode", KioskModePage)
        # etc.
    
    def setup_configurators(self):
        """
        Set up configuration managers with the correct paths.
        
        This should be called after the installation path is confirmed.
        """
        install_path = self.config_data.get('install_path', self.install_path)
        
        # Convert to platform-appropriate path format
        install_path = convert_path_for_platform(install_path)
        
        # Create config directory if it doesn't exist
        config_dir = os.path.join(install_path, 'config')
        os.makedirs(config_dir, exist_ok=True)
        
        # Create metafiles directory if it doesn't exist
        metafiles_dir = os.path.join(install_path, 'src', 'pegasus-fe', 'config', 'metafiles')
        os.makedirs(metafiles_dir, exist_ok=True)
        
        # Initialize configurators
        self.toml_manager = TomlConfigManager(config_dir)
        self.pegasus_manager = PegasusMetadataManager(metafiles_dir)
    
    def perform_installation(self):
        """
        Perform the actual installation based on the wizard configuration.
        
        This is called when the wizard completes.
        
        Returns:
            tuple: (success, message) - Installation success status and message.
        """
        try:
            # Set up configurators if not already done
            if not self.toml_manager or not self.pegasus_manager:
                self.setup_configurators()
            
            # Get final configuration
            config = self.get_config()
            install_path = config.get('install_path', self.install_path)
            
            # Ensure install path exists
            os.makedirs(install_path, exist_ok=True)
            
            # Create default config files
            logger.info(f"Creating default configuration files in {install_path}")
            self.toml_manager.create_default_configs(install_path)
            
            # Create default metadata files
            logger.info(f"Creating default metadata files in {install_path}")
            self.pegasus_manager.create_default_metafiles(install_path)
            
            # Configure dynamic marquee if enabled
            if config.get('dynamic_marquee_enabled', False):
                logger.info("Configuring dynamic marquee")
                self.toml_manager.update_config(
                    'display_config',
                    'dynamic_marquee',
                    'enabled',
                    True
                )
                self.toml_manager.update_config(
                    'display_config',
                    'dynamic_marquee',
                    'display_number',
                    config.get('dynamic_marquee_display', 0)
                )
                if config.get('dynamic_marquee_default_image'):
                    self.toml_manager.update_config(
                        'display_config',
                        'dynamic_marquee',
                        'default_image',
                        config.get('dynamic_marquee_default_image')
                    )
            
            # Configure ITGMania if enabled
            if config.get('itgmania_enabled', False):
                logger.info("Configuring ITGMania")
                itgmania_path = config.get('itgmania_path', '')
                
                if itgmania_path and os.path.exists(itgmania_path):
                    # Add to installed_games.toml
                    self.toml_manager.update_config(
                        'installed_games',
                        'binary_games',
                        'itgmania',
                        {'path': itgmania_path}
                    )
                    
                    # Add to Pegasus metadata
                    self.pegasus_manager.add_game(
                        'metadata.pegasus.txt',
                        {
                            'name': 'ITGMania',
                            'id': 'itgmania',
                            'sort_by': 'itg1',
                            'box_front': '../../../../assets/images/banners/itgmania.png'
                        },
                        install_path
                    )
                    
                    # Configure dynamic marquee for ITGMania if enabled
                    if config.get('itgmania_dynamic_marquee', False):
                        logger.info("Configuring ITGMania dynamic marquee")
                        # Enable ITGMania display in display_config.toml
                        self.toml_manager.update_config(
                            'display_config',
                            'itgmania_display',
                            'enabled',
                            True
                        )
                        
                        # Set up ITGMania dynamic marquee for song banners
                        # This would normally require running the setup script
                        # For now, just log that it needs to be done
                        logger.info("ITGMania dynamic marquee setup needed after installation")
            
            # Configure additional binary games
            if config.get('binary_games'):
                logger.info("Configuring additional binary games")
                for game_id, game_info in config.get('binary_games', {}).items():
                    if 'path' in game_info and os.path.exists(game_info['path']):
                        # Add to installed_games.toml
                        self.toml_manager.update_config(
                            'installed_games',
                            'binary_games',
                            game_id,
                            {'path': game_info['path']}
                        )
                        
                        # Add to Pegasus metadata if needed
                        if game_info.get('add_to_pegasus', True):
                            self.pegasus_manager.add_game(
                                game_info.get('pegasus_file', '2.metadata.pegasus.txt'),
                                {
                                    'name': game_info.get('name', game_id),
                                    'id': game_id,
                                    'sort_by': game_info.get('sort_by', game_id),
                                    'box_front': game_info.get('box_front', '')
                                },
                                install_path
                            )
            
            # Configure MAME games
            if config.get('mame_games'):
                logger.info("Configuring MAME games")
                for game_id, game_info in config.get('mame_games', {}).items():
                    if 'rom' in game_info:
                        # Add to installed_games.toml
                        game_config = {
                            'rom': game_info['rom']
                        }
                        
                        if 'state' in game_info:
                            game_config['state'] = game_info['state']
                        
                        self.toml_manager.update_config(
                            'installed_games',
                            'mame_games',
                            game_id,
                            game_config
                        )
                        
                        # Add to Pegasus metadata if needed
                        if game_info.get('add_to_pegasus', True):
                            self.pegasus_manager.add_game(
                                game_info.get('pegasus_file', '3.metadata.pegasus.txt'),
                                {
                                    'name': game_info.get('name', game_id),
                                    'id': game_id,
                                    'sort_by': game_info.get('sort_by', game_id),
                                    'box_front': game_info.get('box_front', '')
                                },
                                install_path
                            )
            
            # Configure key bindings
            if config.get('key_bindings'):
                logger.info("Configuring key bindings")
                for key, binding in config.get('key_bindings', {}).items():
                    self.toml_manager.update_config(
                        'key_listener',
                        'shortcuts',
                        key,
                        binding
                    )
            
            # Configure utilities
            # Lights
            if config.get('lights_enabled', False):
                logger.info("Configuring lights management")
                self.toml_manager.update_config(
                    'utility_config',
                    'lights',
                    'enabled',
                    True
                )
                
                if config.get('light_reset_executable_path'):
                    self.toml_manager.update_config(
                        'utility_config',
                        'lights',
                        'light_reset_executable_path',
                        config.get('light_reset_executable_path')
                    )
                
                if config.get('light_mame_executable_path'):
                    self.toml_manager.update_config(
                        'utility_config',
                        'lights',
                        'light_mame_executable_path',
                        config.get('light_mame_executable_path')
                    )
            
            # VPN
            if config.get('vpn_enabled', False):
                logger.info("Configuring VPN management")
                self.toml_manager.update_config(
                    'utility_config',
                    'vpn',
                    'enabled',
                    True
                )
                
                for key in ['vpn_application_directory', 'vpn_application', 
                           'vpn_process', 'vpn_config_profile', 'seconds_to_wait']:
                    if key in config:
                        self.toml_manager.update_config(
                            'utility_config',
                            'vpn',
                            key,
                            config.get(key)
                        )
            
            # Streaming
            if config.get('streaming_enabled', False):
                logger.info("Configuring streaming")
                self.toml_manager.update_config(
                    'utility_config',
                    'streaming',
                    'webcam_management_enabled',
                    config.get('webcam_management_enabled', False)
                )
                
                for key in ['webcam_management_executable', 'obs_executable', 'obs_arguments']:
                    if key in config:
                        self.toml_manager.update_config(
                            'utility_config',
                            'streaming',
                            key,
                            config.get(key)
                        )
            
            # Logging
            if config.get('logging_enabled', True):
                logger.info("Configuring logging")
                log_dir = config.get('logging_directory', os.path.join(install_path, 'logs'))
                os.makedirs(log_dir, exist_ok=True)
                
                self.toml_manager.update_config(
                    'default_config',
                    'logging',
                    'logdirectory',
                    log_dir
                )
            
            # Windows-specific configuration
            if sys.platform == 'win32' and config.get('kiosk_mode', False):
                logger.info("Configuring Windows kiosk mode")
                from configurators.os_specific.windows import setup_kiosk_mode
                
                # Get kiosk mode settings
                username = config.get('kiosk_mode_username', '')
                password = config.get('kiosk_mode_password', '')
                
                # Set up kiosk mode
                kiosk_success = setup_kiosk_mode(
                    install_path,
                    username=username if username else None,
                    password=password if password else None
                )
                
                if not kiosk_success:
                    logger.warning("Failed to set up kiosk mode")
            
            # Create desktop shortcut if requested
            if config.get('create_shortcut', True):
                logger.info("Creating desktop shortcut")
                self.create_shortcut(install_path)
            
            logger.info("Installation completed successfully")
            return True, "Installation completed successfully"
            
        except Exception as e:
            logger.exception("Error during installation")
            return False, f"Installation failed: {str(e)}"
    
    def create_shortcut(self, install_path):
        """
        Create a desktop shortcut to launch Arcade Station.
        
        Args:
            install_path (str): Installation path.
        """
        try:
            # Get desktop path
            if sys.platform == 'win32':
                desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
                
                # Create batch file shortcut
                shortcut_path = os.path.join(desktop, 'Arcade Station.bat')
                
                # Create batch file
                with open(shortcut_path, 'w') as f:
                    f.write(f'@echo off\n')
                    f.write(f'cd /d "{install_path}"\n')
                    f.write(f'start arcade_station_start_windows.bat\n')
                
                logger.info(f"Created shortcut at {shortcut_path}")
                
            elif sys.platform == 'darwin':  # macOS
                desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
                
                # Create shell script shortcut
                shortcut_path = os.path.join(desktop, 'Arcade Station.command')
                
                # Create shell script
                with open(shortcut_path, 'w') as f:
                    f.write('#!/bin/bash\n')
                    f.write(f'cd "{install_path}"\n')
                    f.write('./arcade_station_start.sh\n')
                
                # Make it executable
                os.chmod(shortcut_path, 0o755)
                
                logger.info(f"Created shortcut at {shortcut_path}")
                
            else:  # Linux
                desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
                
                # Create .desktop file
                shortcut_path = os.path.join(desktop, 'arcade-station.desktop')
                
                # Create desktop entry
                with open(shortcut_path, 'w') as f:
                    f.write('[Desktop Entry]\n')
                    f.write('Type=Application\n')
                    f.write('Name=Arcade Station\n')
                    f.write(f'Exec={install_path}/arcade_station_start.sh\n')
                    f.write('Terminal=false\n')
                    f.write('Categories=Game\n')
                
                # Make it executable
                os.chmod(shortcut_path, 0o755)
                
                logger.info(f"Created shortcut at {shortcut_path}")
                
        except Exception as e:
            logger.error(f"Failed to create shortcut: {str(e)}")
    
    def exit(self):
        """
        Close the wizard and perform installation if finished.
        """
        # Check if we're on the last page
        if self.current_page == self.page_order[-1]:
            # Perform installation
            success, message = self.perform_installation()
            
            if success:
                # Show success message
                self.show_message(
                    "Installation Complete",
                    "Arcade Station has been installed successfully! You can now start using it.",
                    "info"
                )
            else:
                # Show error message
                self.show_message(
                    "Installation Failed",
                    f"An error occurred during installation: {message}",
                    "error"
                )
        
        # Close the wizard
        super().exit() 