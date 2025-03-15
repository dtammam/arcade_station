"""
Pegasus Metadata Manager for Arcade Station Installer.

This module provides functionality to manipulate Pegasus metadata files
that are used to configure the Pegasus frontend with game entries.
"""

import os
import sys
import logging
import re
from pathlib import Path

# Import core functions
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.core_functions import convert_path_for_platform

logger = logging.getLogger("ArcadeStationInstaller")

class PegasusMetadataManager:
    """
    Manages Pegasus frontend metadata files for the Arcade Station installer.
    
    This class provides methods to read, write, and update Pegasus metadata files
    that define the games shown in the Pegasus frontend.
    """
    
    def __init__(self, metafiles_dir):
        """
        Initialize the metadata manager.
        
        Args:
            metafiles_dir (str): Path to the directory containing metadata files.
        """
        self.metafiles_dir = metafiles_dir
        # Ensure the directory exists
        os.makedirs(metafiles_dir, exist_ok=True)
    
    def get_metafile_path(self, filename):
        """
        Get the full path to a metadata file.
        
        Args:
            filename (str): Name of the metadata file.
            
        Returns:
            str: Full path to the metadata file.
        """
        # Handle the file naming convention (metadata.pegasus.txt or X.metadata.pegasus.txt)
        if not filename.endswith('.pegasus.txt'):
            if re.match(r'^\d+$', filename):  # Check if it's just a number
                filename = f"{filename}.metadata.pegasus.txt"
            else:
                filename = f"metadata.pegasus.txt"
                
        return os.path.join(self.metafiles_dir, filename)
    
    def read_metafile(self, filename):
        """
        Read a Pegasus metadata file.
        
        Args:
            filename (str): Name of the metadata file.
            
        Returns:
            str: Content of the metadata file.
        """
        path = self.get_metafile_path(filename)
        
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.warning(f"Metadata file not found: {path}")
                return ""
        except Exception as e:
            logger.error(f"Error reading metadata file {path}: {str(e)}")
            return ""
    
    def write_metafile(self, filename, content):
        """
        Write content to a Pegasus metadata file.
        
        Args:
            filename (str): Name of the metadata file.
            content (str): Content to write to the file.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        path = self.get_metafile_path(filename)
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.info(f"Successfully wrote metadata to {path}")
            return True
        except Exception as e:
            logger.error(f"Error writing metadata file {path}: {str(e)}")
            return False
    
    def parse_metafile(self, content):
        """
        Parse a Pegasus metadata file into a structured format.
        
        Args:
            content (str): Content of the metadata file.
            
        Returns:
            dict: Parsed metadata structure.
        """
        metadata = {
            'collection': None,
            'shortname': None,
            'games': []
        }
        
        current_game = None
        
        # Split the content into lines and process line by line
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
                
            # Check for collection and shortname
            if line.startswith('collection:'):
                metadata['collection'] = line.split(':', 1)[1].strip()
            elif line.startswith('shortname:'):
                metadata['shortname'] = line.split(':', 1)[1].strip()
            # Check for game entries
            elif line.startswith('game:'):
                # If there was a previous game, add it to the list
                if current_game is not None:
                    metadata['games'].append(current_game)
                
                # Start a new game entry
                current_game = {
                    'name': line.split(':', 1)[1].strip(),
                    'file': None,
                    'sortBy': None,
                    'launch': [],
                    'assets': {}
                }
            # Check for file entry
            elif line.startswith('file:') and current_game is not None:
                current_game['file'] = line.split(':', 1)[1].strip()
            # Check for sortBy entry
            elif line.startswith('sortBy:') and current_game is not None:
                current_game['sortBy'] = line.split(':', 1)[1].strip()
            # Check for launch entries
            elif line.startswith('launch:') and current_game is not None:
                # Launch will be followed by multiple lines
                current_game['launch'] = []
            elif current_game is not None and len(current_game['launch']) < 3 and not line.startswith('assets.'):
                # This is a continuation of the launch command (limited to 3 lines)
                # Skip lines that are asset definitions
                if current_game['launch'] or line.strip():  # Only add non-empty lines or if we've already started adding launch commands
                    current_game['launch'].append(line.strip())
            # Check for asset entries
            elif line.startswith('assets.') and current_game is not None:
                asset_type, value = line.split(':', 1)
                asset_type = asset_type.split('.', 1)[1].strip()  # Remove 'assets.' prefix
                current_game['assets'][asset_type] = value.strip()
        
        # Don't forget to add the last game
        if current_game is not None:
            metadata['games'].append(current_game)
            
        return metadata
    
    def generate_metafile_content(self, metadata):
        """
        Generate content for a Pegasus metadata file from a structured format.
        
        Args:
            metadata (dict): Parsed metadata structure.
            
        Returns:
            str: Generated metadata file content.
        """
        lines = []
        
        # Add collection and shortname
        if metadata.get('collection'):
            lines.append(f"collection: {metadata['collection']}")
        if metadata.get('shortname'):
            lines.append(f"shortname: {metadata['shortname']}")
            
        lines.append("")  # Empty line for readability
        
        # Add games
        for game in metadata.get('games', []):
            lines.append(f"game: {game['name']}")
            
            if game.get('file'):
                lines.append(f"file: {game['file']}")
                
            if game.get('sortBy'):
                lines.append(f"sortBy: {game['sortBy']}")
                
            if game.get('launch'):
                lines.append("launch:")
                for launch_line in game['launch']:
                    lines.append(f"    {launch_line}")
                    
            # Add assets
            for asset_type, asset_path in game.get('assets', {}).items():
                lines.append(f"assets.{asset_type}: {asset_path}")
                
            lines.append("")  # Empty line between games
            
        return '\n'.join(lines)
    
    def add_game(self, metafile, game_info, install_path, python_exe=None):
        """
        Add a game entry to a Pegasus metadata file.
        
        Args:
            metafile (str): Name of the metadata file.
            game_info (dict): Information about the game to add.
            install_path (str): Installation path for Arcade Station.
            python_exe (str, optional): Path to the Python executable. 
                                         If None, uses the current Python.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Read and parse the existing metadata file
            content = self.read_metafile(metafile)
            metadata = self.parse_metafile(content)
            
            # Check if the game already exists
            for game in metadata['games']:
                if game['name'] == game_info['name']:
                    logger.warning(f"Game '{game_info['name']}' already exists in {metafile}")
                    return False
            
            # Convert paths for the current platform
            install_path = convert_path_for_platform(install_path)
            
            # Determine Python executable path
            if python_exe is None:
                if sys.platform == 'win32':
                    python_exe = os.path.join(install_path, '.venv', 'Scripts', 'pythonw.exe')
                else:
                    python_exe = os.path.join(install_path, '.venv', 'bin', 'python')
                    
            # Create launch command
            launcher_script = os.path.join(install_path, 'src', 'arcade_station', 'launchers', 'launch_game.py')
            
            # Create new game entry
            new_game = {
                'name': game_info['name'],
                'file': f"not\\using\\files\\to\\launch\\games\\{game_info['name']}",
                'sortBy': game_info['sort_by'],
                'launch': [
                    f'"{python_exe}"',
                    f'"{launcher_script}"',
                    f'"{game_info["id"]}"'
                ],
                'assets': {
                    'box_front': game_info['box_front']
                }
            }
            
            # Add the new game to the metadata
            metadata['games'].append(new_game)
            
            # Generate and write the updated content
            updated_content = self.generate_metafile_content(metadata)
            success = self.write_metafile(metafile, updated_content)
            
            if success:
                logger.info(f"Successfully added game '{game_info['name']}' to {metafile}")
                return True
            else:
                logger.error(f"Failed to write updated metadata for game '{game_info['name']}' to {metafile}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding game to metadata file: {str(e)}")
            return False
    
    def remove_game(self, metafile, game_name):
        """
        Remove a game entry from a Pegasus metadata file.
        
        Args:
            metafile (str): Name of the metadata file.
            game_name (str): Name of the game to remove.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Read and parse the existing metadata file
            content = self.read_metafile(metafile)
            metadata = self.parse_metafile(content)
            
            # Find and remove the game
            original_count = len(metadata['games'])
            metadata['games'] = [game for game in metadata['games'] if game['name'] != game_name]
            
            # Check if any games were removed
            if len(metadata['games']) == original_count:
                logger.warning(f"Game '{game_name}' not found in {metafile}")
                return False
            
            # Generate and write the updated content
            updated_content = self.generate_metafile_content(metadata)
            success = self.write_metafile(metafile, updated_content)
            
            if success:
                logger.info(f"Successfully removed game '{game_name}' from {metafile}")
                return True
            else:
                logger.error(f"Failed to write updated metadata after removing game '{game_name}' from {metafile}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing game from metadata file: {str(e)}")
            return False
    
    def create_default_metafiles(self, install_path):
        """
        Create default Pegasus metadata files for a fresh installation.
        
        Args:
            install_path (str): Installation path for Arcade Station.
            
        Returns:
            bool: True if all files were created successfully, False otherwise.
        """
        success = True
        install_path = convert_path_for_platform(install_path)
        
        # Main metadata file for rhythm games
        main_metadata = {
            'collection': 'Rhythm Games',
            'shortname': 'rhythm',
            'games': []
        }
        
        # DDR metadata file
        ddr_metadata = {
            'collection': 'Dance Dance Revolution',
            'shortname': 'ddr',
            'games': []
        }
        
        # Dancing Stage metadata file
        ds_metadata = {
            'collection': 'Dancing Stage',
            'shortname': 'ds',
            'games': []
        }
        
        # Write the metadata files
        if not self.write_metafile('metadata.pegasus.txt', self.generate_metafile_content(main_metadata)):
            success = False
            
        if not self.write_metafile('2.metadata.pegasus.txt', self.generate_metafile_content(ddr_metadata)):
            success = False
            
        if not self.write_metafile('3.metadata.pegasus.txt', self.generate_metafile_content(ds_metadata)):
            success = False
            
        return success 