"""
Installation manager for handling the Arcade Station installation process
"""
import os
import shutil
import platform
import logging
from pathlib import Path
import tomllib
from typing import Dict, Any, Optional, List, Tuple

# Try to import tomli_w for writing TOML files
try:
    import tomli_w
except ImportError:
    # If tomli_w is not available, we'll handle it when writing TOML files
    pass

from .. import IS_WINDOWS, IS_LINUX, IS_MAC, INSTALLER_DIR, RESOURCES_DIR
from ..utils.game_id import get_display_name

class InstallationManager:
    """Manages the Arcade Station installation process."""
    
    def __init__(self):
        """Initialize the installation manager."""
        self.is_windows = IS_WINDOWS
        self.is_linux = IS_LINUX
        self.is_mac = IS_MAC
        self.resources_dir = RESOURCES_DIR
        self.files_copied = False  # Track if files have been copied
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(os.path.join(os.path.dirname(INSTALLER_DIR), "installation.log"))
            ]
        )
        self.logger = logging.getLogger("InstallationManager")
    
    def check_if_installed(self) -> bool:
        """Check if Arcade Station is already installed.
        
        Returns:
            bool: True if installed, False otherwise
        """
        # Check for common installation markers
        markers = [
            self._find_existing_config_dir(),
            self._find_startup_entry() if self.is_windows else False
        ]
        
        return any(markers)
    
    def check_if_installed_at_path(self, path: str) -> bool:
        """Check if Arcade Station is installed at the specified path.
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if installed at path, False otherwise
        """
        if not path or not os.path.isdir(path):
            return False
            
        # Check for config directory and expected files
        config_dir = os.path.join(path, "config")
        return os.path.isdir(config_dir) and self._check_config_files(config_dir)
    
    def _find_existing_config_dir(self) -> bool:
        """Check for existing configuration directory.
        
        Returns:
            bool: True if found, False otherwise
        """
        # Check common locations
        possible_locations = [
            os.path.expanduser("~/arcade_station"),
            os.path.expanduser("~/Arcade Station"),
            "C:/arcade_station",
            "C:/Arcade Station",
            "/opt/arcade_station",
            "/usr/local/arcade_station",
            os.path.expanduser("~/Applications/Arcade Station.app"),
            "/Applications/Arcade Station.app"
        ]
        
        for location in possible_locations:
            config_dir = os.path.join(location, "config")
            if os.path.isdir(config_dir) and self._check_config_files(config_dir):
                return True
        
        return False
    
    def _check_config_files(self, config_dir: str) -> bool:
        """Check if a directory contains Arcade Station config files.
        
        Args:
            config_dir: Directory to check
            
        Returns:
            bool: True if it contains expected config files
        """
        expected_files = [
            "default_config.toml",
            "display_config.toml",
            "installed_games.toml"
        ]
        
        return any(os.path.isfile(os.path.join(config_dir, f)) for f in expected_files)
    
    def _find_startup_entry(self) -> bool:
        """Check for Windows startup entry.
        
        Returns:
            bool: True if found, False otherwise
        """
        if not self.is_windows:
            return False
            
        try:
            import winreg
            startup_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            )
            
            try:
                value, _ = winreg.QueryValueEx(startup_key, "ArcadeStation")
                return "arcade_station" in value.lower()
            except FileNotFoundError:
                return False
            finally:
                winreg.CloseKey(startup_key)
        except Exception:
            return False
    
    def get_current_install_path(self) -> str:
        """Get the current installation path if it exists.
        
        Returns:
            str: Current install path or empty string if not found
        """
        # Check common locations from _find_existing_config_dir
        possible_locations = [
            os.path.expanduser("~/arcade_station"),
            os.path.expanduser("~/Arcade Station"),
            "C:/arcade_station",
            "C:/Arcade Station",
            "/opt/arcade_station",
            "/usr/local/arcade_station"
        ]
        
        if self.is_mac:
            possible_locations.extend([
                os.path.expanduser("~/Applications/Arcade Station.app/Contents/Resources"),
                "/Applications/Arcade Station.app/Contents/Resources"
            ])
        
        for location in possible_locations:
            config_dir = os.path.join(location, "config")
            if os.path.isdir(config_dir) and self._check_config_files(config_dir):
                return location
        
        return ""
    
    def get_suggested_install_path(self) -> str:
        """Get a suggested installation path for a new installation.
        
        Returns:
            str: Suggested install path
        """
        if self.is_windows:
            return os.path.join(os.path.expanduser("~"), "Arcade Station")
        elif self.is_linux:
            return os.path.join(os.path.expanduser("~"), "arcade_station")
        elif self.is_mac:
            return os.path.join(os.path.expanduser("~"), "Applications", "Arcade Station")
        else:
            return os.path.join(os.path.expanduser("~"), "arcade_station")
    
    def get_monitor_count(self) -> int:
        """Get the number of monitors.
        
        Returns:
            int: Number of detected monitors, defaults to 1
        """
        try:
            if self.is_windows:
                import ctypes
                user32 = ctypes.windll.user32
                return user32.GetSystemMetrics(80)  # SM_CMONITORS
            else:
                # For Linux/Mac, try using screeninfo if available
                try:
                    import screeninfo
                    return len(screeninfo.get_monitors())
                except (ImportError, Exception):
                    # Default to 1 if detection fails
                    return 1
        except Exception:
            return 1
    
    def perform_installation(self, config: Dict[str, Any]) -> bool:
        """Perform the installation.
        
        Args:
            config: User configuration from the wizard
            
        Returns:
            bool: True if installation successful, False otherwise
        """
        try:
            install_path = config.get("install_path")
            if not install_path:
                self.logger.error("No installation path specified")
                return False
            
            self.logger.info(f"Starting installation to {install_path}")
            
            # Create installation directory structure
            os.makedirs(install_path, exist_ok=True)
            
            # Get source directory (where our project files are)
            src_dir = os.path.join(install_path, "src")
            os.makedirs(src_dir, exist_ok=True)
            
            # Create config directory
            config_dir = os.path.join(install_path, "config")
            os.makedirs(config_dir, exist_ok=True)
            
            # Create venv directory
            venv_dir = os.path.join(install_path, ".venv")
            os.makedirs(venv_dir, exist_ok=True)
            
            # Create core directories
            arcade_station_dir = os.path.join(src_dir, "arcade_station")
            os.makedirs(arcade_station_dir, exist_ok=True)
            
            pegasus_dir = os.path.join(src_dir, "pegasus-fe")
            os.makedirs(pegasus_dir, exist_ok=True)
            
            pegasus_config_dir = os.path.join(pegasus_dir, "config")
            os.makedirs(pegasus_config_dir, exist_ok=True)
            
            pegasus_metafiles_dir = os.path.join(pegasus_config_dir, "metafiles")
            os.makedirs(pegasus_metafiles_dir, exist_ok=True)
            
            # Create the assets directory
            assets_dir = os.path.join(install_path, "assets")
            os.makedirs(os.path.join(assets_dir, "images", "banners"), exist_ok=True)
            
            # Copy project files to installation directory if not already done
            if not self.files_copied:
                self._copy_project_files(install_path)
            else:
                self.logger.info("Project files already copied, skipping copy step")
            
            # Generate configuration files
            self._generate_config_files(config, config_dir)
            
            # Generate Pegasus metadata
            self._generate_pegasus_metadata(config, pegasus_metafiles_dir)
            
            # Setup platform-specific items
            if self.is_windows:
                self._setup_windows_specific(config, install_path)
            elif self.is_linux:
                self._setup_linux_specific(config, install_path)
            elif self.is_mac:
                self._setup_mac_specific(config, install_path)
            
            self.logger.info(f"Arcade Station installation completed successfully to {install_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error during installation: {str(e)}", exc_info=True)
            return False

    def _copy_project_files(self, install_path: str) -> None:
        """Copy project files to the installation directory.
        
        Args:
            install_path: Path to install directory
        """
        try:
            import shutil
            import os
            from pathlib import Path
            
            # Get the current directory (where the installer is running from)
            current_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
            
            # Log the process
            self.logger.info(f"Starting to copy all project files from {current_dir} to {install_path}")
            
            # Get all items in the current directory
            all_items = list(current_dir.iterdir())
            
            # Tracking for logs
            total_dirs_copied = 0
            total_files_copied = 0
            
            # Copy each item
            for item in all_items:
                # Skip the installer for now to avoid copying it while it's running
                if item.name == "arcade_station_installer":
                    continue
                    
                dst_path = Path(install_path) / item.name
                
                self.logger.info(f"Copying {item.name} to {dst_path}")
                
                # Remove destination if it exists
                if dst_path.exists():
                    if dst_path.is_dir():
                        shutil.rmtree(dst_path)
                    else:
                        os.remove(dst_path)
                
                # Copy directory or file with detailed logging
                if item.is_dir():
                    # Create custom copy function for counting items
                    def copy_dir_recursive(src, dst):
                        nonlocal total_dirs_copied, total_files_copied
                        if os.path.isdir(src):
                            total_dirs_copied += 1
                            os.makedirs(dst, exist_ok=True)
                            self.logger.info(f"Copying directory: {os.path.basename(src)}")
                            items = os.listdir(src)
                            for item in items:
                                s = os.path.join(src, item)
                                d = os.path.join(dst, item)
                                copy_dir_recursive(s, d)
                        else:
                            total_files_copied += 1
                            shutil.copy2(src, dst)
                    
                    # Use our custom copy function
                    copy_dir_recursive(str(item), str(dst_path))
                else:
                    shutil.copy2(item, dst_path)
                    total_files_copied += 1
            
            # Now copy the installer directory without the running executable
            installer_src = current_dir / "arcade_station_installer"
            installer_dst = Path(install_path) / "arcade_station_installer"
            
            if installer_src.exists():
                self.logger.info("Copying installer files...")
                
                # Create the destination directory
                os.makedirs(installer_dst, exist_ok=True)
                
                # Copy all files and subdirectories in installer
                for item in installer_src.iterdir():
                    dst_item = installer_dst / item.name
                    try:
                        if item.is_dir():
                            # Custom function to copy installer directories
                            def copy_installer_dir(src, dst):
                                nonlocal total_dirs_copied, total_files_copied
                                os.makedirs(dst, exist_ok=True)
                                total_dirs_copied += 1
                                
                                for item in os.listdir(src):
                                    s = os.path.join(src, item)
                                    d = os.path.join(dst, item)
                                    
                                    if os.path.isdir(s):
                                        copy_installer_dir(s, d)
                                    else:
                                        try:
                                            shutil.copy2(s, d)
                                            total_files_copied += 1
                                        except (PermissionError, OSError) as e:
                                            self.logger.warning(f"Skipping locked file: {os.path.basename(s)}")
                            
                            copy_installer_dir(str(item), str(dst_item))
                        else:
                            try:
                                shutil.copy2(item, dst_item)
                                total_files_copied += 1
                            except (PermissionError, OSError):
                                self.logger.warning(f"Skipping locked file: {item.name}")
                    except Exception as e:
                        self.logger.error(f"Error copying {item.name}: {str(e)}")
            
            # Ensure these specific directories exist even if not in source
            required_dirs = [
                "src/arcade_station",
                "src/pegasus-fe/config/metafiles",
                "config",
                "assets/images/banners",
                ".venv"
            ]
            
            for dir_path in required_dirs:
                dir_full_path = Path(install_path) / dir_path
                if not dir_full_path.exists():
                    self.logger.info(f"Creating required directory: {dir_path}")
                    os.makedirs(dir_full_path, exist_ok=True)
            
            self.logger.info(f"Project files copied successfully: {total_dirs_copied} directories and {total_files_copied} files")
            self.files_copied = True  # Mark files as copied
        except Exception as e:
            self.logger.error(f"Error copying project files: {str(e)}", exc_info=True)
            raise
    
    def _generate_config_files(self, config: Dict[str, Any], config_dir: str) -> None:
        """Generate the configuration files.
        
        Args:
            config: User configuration from the wizard
            config_dir: Directory to write the configuration files
        """
        # Generate default_config.toml
        log_dir = os.path.join(config_dir, "logs")
        if config.get("log_dir"):
            log_dir = config.get("log_dir")
            
        # Create the log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
            
        default_config = {
            "logging": {
                "logdirectory": log_dir
            },
            "paths": {
                "pegasus_base_path": "../../../pegasus-fe"
            }
        }
        self._write_toml(os.path.join(config_dir, "default_config.toml"), default_config)
        
        # Generate display_config.toml
        display_config = {
            "display": {
                "image_path": os.path.join(config["install_path"], "assets", "images", "banners", "arcade_station.png"),
                "default_image_path": config.get("default_marquee_image", ""),
                "background_color": config.get("marquee_background_color", "black"),
                "monitor_index": config.get("marquee_monitor", 1)
            },
            "dynamic_marquee": {
                "enabled": config.get("use_dynamic_marquee", True),
                "itgmania_display_enabled": config.get("enable_itgmania_display", True),
                "itgmania_display_file_path": "",
                "itgmania_base_path": "",
                "itgmania_banner_path": ""
            }
        }
        
        # If using default image, make sure the path is set to the standard location
        if config.get("use_default_marquee_image", True):
            display_config["display"]["default_image_path"] = os.path.join(
                config["install_path"], "assets", "images", "banners", "arcade_station.png"
            )
        
        # Update ITGMania paths if configured
        if config.get("itgmania", {}).get("enabled", False):
            display_config["dynamic_marquee"]["itgmania_base_path"] = config["itgmania"]["path"]
            display_config["dynamic_marquee"]["itgmania_display_file_path"] = os.path.join(
                config["itgmania"]["path"], "Themes", "Simply Love", "Modules", "ArcadeStationMarquee.log"
            )
            
            # Set banner path based on whether using default or custom
            if config["itgmania"].get("use_default_image", True):
                display_config["dynamic_marquee"]["itgmania_banner_path"] = os.path.join(
                    config["install_path"], "assets", "images", "banners", "simply-love.png"
                )
            elif config["itgmania"].get("custom_image"):
                display_config["dynamic_marquee"]["itgmania_banner_path"] = config["itgmania"]["custom_image"]
        
        self._write_toml(os.path.join(config_dir, "display_config.toml"), display_config)
        
        # Generate installed_games.toml
        installed_games = {
            "games": {}
        }
        
        # Add ITGMania if configured from either source
        if config.get("itgmania", {}).get("enabled", False):
            itg_path = config["itgmania"]["path"]
            
            # Determine image path
            itg_image = ""
            if config["itgmania"].get("use_default_image", True):
                itg_image = os.path.join(config["install_path"], "assets", "images", "banners", "simply-love.png")
            elif config["itgmania"].get("custom_image"):
                itg_image = config["itgmania"]["custom_image"]
                
            installed_games["games"]["itgmania"] = {
                "path": itg_path,
                "banner": itg_image
            }
            
        # Also check binary_games for ITGMania as a fallback
        elif config.get("binary_games", {}).get("itgmania"):
            game_info = config["binary_games"]["itgmania"]
            installed_games["games"]["itgmania"] = {
                "path": game_info["path"],
                "banner": game_info.get("banner", "")
            }
        
        # Add other binary games if configured
        if config.get("binary_games"):
            for game_id, game_info in config["binary_games"].items():
                if game_id == "itgmania":
                    continue
                    
                installed_games["games"][game_id] = {
                    "display_name": game_info["display_name"],
                    "path": game_info["path"],
                    "banner": game_info.get("banner", "")
                }
        
        # Add MAME games if configured
        if config.get("mame_games"):
            for game_id, game_info in config["mame_games"].items():
                installed_games["games"][game_id] = {
                    "display_name": game_info["display_name"],
                    "rom": game_info["rom"],
                    "state": game_info.get("state", "o"),
                    "banner": game_info.get("banner", "")
                }
        
        self._write_toml(os.path.join(config_dir, "installed_games.toml"), installed_games)
        
        # Generate key_listener.toml
        key_listener = {
            "key_mappings": config.get("key_listener", {}).get("key_mappings", {})
        }
        
        # If no key bindings were provided in the configuration, set default ones
        if not key_listener["key_mappings"]:
            key_listener["key_mappings"] = {
                "ctrl+space": "../arcade_station/core/common/kill_all_and_reset_pegasus.py"
            }
            
        self._write_toml(os.path.join(config_dir, "key_listener.toml"), key_listener)
        
        # Generate processes_to_kill.toml
        processes_to_kill = {
            "processes": {
                "names": [
                    "cmd",
                    "explorer",
                    "gslauncher",
                    "In The Groove",
                    "ITGmania",
                    "i_view64",
                    "LightsTest",
                    "mame",
                    "mame2lit",
                    "mame_lights",
                    "mmc",
                    "notepad",
                    "notepad++",
                    "NotITG-v4.2.0",
                    "OpenITG",
                    "OpenITG-PC",
                    "outfox",
                    "pegasus-fe_windows",
                    "regedit",
                    "spice",
                    "StepMania",
                    "Taskmgr",
                    "timeout",
                    "marquee_image"
                ]
            }
        }
        self._write_toml(os.path.join(config_dir, "processes_to_kill.toml"), processes_to_kill)
        
        # Generate MAME config if MAME games are configured
        if config.get("mame_path"):
            mame_config = {
                "mame": {
                    "path": config["mame_path"],
                    "exe": "mame.exe" if self.is_windows else "mame",
                    "inipath": config.get("mame_inipath", "")
                }
            }
            self._write_toml(os.path.join(config_dir, "mame_config.toml"), mame_config)
        
        # Generate screenshot config
        screenshot_config = {
            "screenshot": {
                "monitor_index": config.get("screenshot_monitor", 0),
                "file_location": os.path.join(config["install_path"], "screenshots"),
                "file_name": "",
                "quality": "High",
                "sound_file": os.path.join(config["install_path"], "assets", "sounds", "megatouch_yahoo.wav")
            },
            "icloud_upload": {
                "enabled": config.get("use_icloud", False),
                "interval_seconds": 360,
                "delete_after_upload": True,
                "upload_directory": os.path.join(config["install_path"], "screenshots"),
                "apple_services_path": "C:/Program Files (x86)/Common Files/Apple/Internet Services/",
                "processes_to_restart": [
                    "iCloudServices",
                    "iCloudPhotos"
                ]
            }
        }
        self._write_toml(os.path.join(config_dir, "screenshot_config.toml"), screenshot_config)
        
        # Generate utility config
        utility_config = {}
        
        # Use the values from the utilities config if provided
        if "utilities" in config:
            utility_config = config["utilities"]
        else:
            # Fallback to defaults if not provided
            utility_config = {
                "lights": {
                    "enabled": False,
                    "light_reset_executable_path": "",
                    "light_mame_executable_path": ""
                },
                "streaming": {
                    "webcam_management_enabled": False,
                    "webcam_management_executable": "",
                    "obs_executable": config.get("obs_path", ""),
                    "obs_arguments": "--startstreaming --disable-shutdown-check"
                },
                "vpn": {
                    "enabled": config.get("enable_vpn", False),
                    "vpn_application_directory": config.get("vpn_path", ""),
                    "vpn_application": "openvpn-gui.exe",
                    "vpn_process": "openvpn",
                    "vpn_config_profile": "",
                    "seconds_to_wait": 10
                },
                "osd": {
                    "enabled": config.get("enable_volume_control", False) and self.is_windows,
                    "sound_osd_executable": config.get("audio_switcher_path", "")
                }
            }
        self._write_toml(os.path.join(config_dir, "utility_config.toml"), utility_config)
        
        # Generate Pegasus binaries config
        pegasus_binaries = {
            "pegasus": {
                "windows_binary": "pegasus-fe_windows.exe",
                "mac_binary": "pegasus-fe_mac",
                "linux_binary": "pegasus-fe_linux"
            }
        }
        self._write_toml(os.path.join(config_dir, "pegasus_binaries.toml"), pegasus_binaries)
    
    def _generate_pegasus_metadata(self, config: Dict[str, Any], metadata_dir: str) -> None:
        """Generate the Pegasus metadata files.
        
        Args:
            config: User configuration from the wizard
            metadata_dir: Directory to write the metadata files
        """
        # Basic template for metadata.pegasus.txt
        metadata_content = """collection: arcade_station
shortname: arcade_station

"""
        
        # Add ITGMania if configured
        # Check first in itgmania config, then in binary_games as fallback
        itgmania_configured = False
        if config.get("itgmania", {}).get("enabled", False):
            itgmania_path = config["itgmania"].get("path", "")
            
            if itgmania_path:
                launcher_path = os.path.join(config["install_path"], "src", "arcade_station", "launchers", "launch_game.py")
                python_path = os.path.join(config["install_path"], ".venv", "Scripts", "pythonw.exe" if self.is_windows else "python")
                
                # Determine banner image path
                banner_path = "../../../../assets/images/banners/simply-love.png"
                if config["itgmania"].get("custom_image"):
                    custom_banner = config["itgmania"].get("custom_image", "")
                    if custom_banner:
                        # For custom images, use absolute path
                        banner_path = custom_banner.replace("\\", "/")
                elif config["itgmania"].get("use_default_image", True):
                    # For default image, use relative path
                    banner_path = "../../../../assets/images/banners/simply-love.png"
                
                metadata_content += """game: ITGMania
file: not\\using\\files\\to\\launch\\games\\ITGMania
sortBy: a
launch: 
    "{}" 
    "{}" 
    "itgmania"
assets.box_front: {}

""".format(python_path, launcher_path, banner_path)
                itgmania_configured = True
        
        # Add ITGMania from binary_games if not already added
        if not itgmania_configured and config.get("binary_games", {}).get("itgmania"):
            game_id = "itgmania"
            game_info = config["binary_games"]["itgmania"]
            display_name = game_info.get("display_name", "ITGMania")
            
            launcher_path = os.path.join(config["install_path"], "src", "arcade_station", "launchers", "launch_game.py")
            python_path = os.path.join(config["install_path"], ".venv", "Scripts", "pythonw.exe" if self.is_windows else "python")
            
            # Use absolute path for custom banner, relative for default
            asset_path = game_info.get("banner", "")
            if not asset_path:
                asset_path = "../../../../assets/images/banners/simply-love.png"
            else:
                asset_path = asset_path.replace("\\", "/")
            
            metadata_content += """game: {}
file: not\\using\\files\\to\\launch\\games\\{}
sortBy: {}
launch: 
    "{}" 
    "{}" 
    "{}"
assets.box_front: {}

""".format(display_name, display_name, "a", python_path, launcher_path, game_id, asset_path)
        
        # Add other binary games if configured
        if config.get("binary_games"):
            launcher_path = os.path.join(config["install_path"], "src", "arcade_station", "launchers", "launch_game.py")
            python_path = os.path.join(config["install_path"], ".venv", "Scripts", "pythonw.exe" if self.is_windows else "python")
            
            for idx, (game_id, game_info) in enumerate(config["binary_games"].items()):
                # Skip ITGMania as it was already added above
                if game_id == "itgmania":
                    continue
                    
                display_name = game_info.get("display_name", get_display_name(game_id))
                # Use absolute path for custom banner, omit if no banner
                asset_path = game_info.get("banner", "")
                if asset_path:
                    asset_path = asset_path.replace("\\", "/")
                    asset_line = f"assets.box_front: {asset_path}\n"
                else:
                    asset_line = ""
                
                sort_char = chr(ord('b') + idx)  # start with 'b' for binary games
                
                metadata_content += """game: {}
file: not\\using\\files\\to\\launch\\games\\{}
sortBy: {}
launch: 
    "{}" 
    "{}" 
    "{}"
{}

""".format(display_name, display_name, sort_char, python_path, launcher_path, game_id, asset_line)
        
        # Add MAME games if configured
        if config.get("mame_games"):
            launcher_path = os.path.join(config["install_path"], "src", "arcade_station", "launchers", "launch_game.py")
            python_path = os.path.join(config["install_path"], ".venv", "Scripts", "pythonw.exe" if self.is_windows else "python")
            
            for idx, (game_id, game_info) in enumerate(config["mame_games"].items()):
                display_name = game_info.get("display_name", game_id.replace("_", " ").title())
                asset_path = game_info.get("banner", "").replace(config["install_path"], "../..")
                if not asset_path:
                    asset_path = "../../../../assets/images/banners/arcade_station.png"
                
                sort_char = chr(ord('m') + idx)  # start with 'm' for MAME games
                
                metadata_content += """game: {}
file: not\\using\\files\\to\\launch\\games\\{}
sortBy: {}
launch: 
    "{}" 
    "{}" 
    "{}"
assets.box_front: {}

""".format(display_name, display_name, sort_char, python_path, launcher_path, game_id, asset_path)
        
        # Write the metadata file
        metadata_path = os.path.join(metadata_dir, "metadata.pegasus.txt")
        with open(metadata_path, "w", encoding="utf-8") as f:
            f.write(metadata_content)
    
    def _setup_windows_specific(self, config: Dict[str, Any], install_path: str) -> None:
        """Set up Windows-specific components.
        
        Args:
            config: User configuration from the wizard
            install_path: Installation directory
        """
        # Set up auto-logon if kiosk mode is enabled
        if config.get("enable_kiosk_mode"):
            self._setup_windows_autologon(
                config.get("kiosk_username", ""),
                config.get("kiosk_password", "")
            )
            
            # Replace explorer.exe with Arcade Station if requested
            if config.get("kiosk_replace_shell"):
                self._setup_windows_shell_replacement(install_path)
    
    def _setup_windows_autologon(self, username: str, password: str) -> None:
        """Set up Windows auto-logon.
        
        Args:
            username: Username for auto-logon
            password: Password for auto-logon
        """
        if not (username and self.is_windows):
            return
            
        try:
            import winreg
            reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
            
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, 
                               winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "DefaultUserName", 0, winreg.REG_SZ, username)
                winreg.SetValueEx(key, "DefaultPassword", 0, winreg.REG_SZ, password)
                winreg.SetValueEx(key, "AutoAdminLogon", 0, winreg.REG_SZ, "1")
            
            self.logger.info(f"Configured Windows auto-logon for user '{username}'")
        except Exception as e:
            self.logger.error(f"Error setting up auto-logon: {str(e)}")
    
    def _setup_windows_shell_replacement(self, install_path: str) -> None:
        """Set up Windows shell replacement.
        
        Args:
            install_path: Installation directory
        """
        if not self.is_windows:
            return
            
        try:
            import winreg
            
            # Create a startup script
            startup_path = os.path.join(install_path, "start_arcade_station.bat")
            startup_content = f"""@echo off
cd /d "{install_path}"
start "" ".venv\\Scripts\\pythonw.exe" "src\\arcade_station\\core\\common\\start_pegasus.py"
"""
            with open(startup_path, "w") as f:
                f.write(startup_content)
                
            # Register as shell replacement
            shell_reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, shell_reg_path, 0, 
                               winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "Shell", 0, winreg.REG_SZ, startup_path)
            
            # Also add to startup for non-shell replacement mode
            startup_reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, startup_reg_path, 0, 
                               winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "ArcadeStation", 0, winreg.REG_SZ, startup_path)
                
            self.logger.info("Configured Windows shell replacement")
        except Exception as e:
            self.logger.error(f"Error setting up shell replacement: {str(e)}")
    
    def _setup_linux_specific(self, config: Dict[str, Any], install_path: str) -> None:
        """Set up Linux-specific components.
        
        Args:
            config: User configuration from the wizard
            install_path: Installation directory
        """
        # Create a desktop entry for autostart
        autostart_dir = os.path.expanduser("~/.config/autostart")
        os.makedirs(autostart_dir, exist_ok=True)
        
        desktop_entry = os.path.join(autostart_dir, "arcade_station.desktop")
        entry_content = f"""[Desktop Entry]
Type=Application
Name=Arcade Station
Comment=Arcade Station Frontend
Exec=bash -c "cd {install_path} && .venv/bin/python src/arcade_station/core/common/start_pegasus.py"
Terminal=false
Categories=Game;
"""
        
        with open(desktop_entry, "w") as f:
            f.write(entry_content)
            
        # Make the file executable
        os.chmod(desktop_entry, 0o755)
        
        self.logger.info("Created Linux autostart entry")
    
    def _setup_mac_specific(self, config: Dict[str, Any], install_path: str) -> None:
        """Set up Mac-specific components.
        
        Args:
            config: User configuration from the wizard
            install_path: Installation directory
        """
        # Create a launch agent for autostart
        launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
        os.makedirs(launch_agents_dir, exist_ok=True)
        
        plist_file = os.path.join(launch_agents_dir, "com.arcadestation.startup.plist")
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.arcadestation.startup</string>
    <key>ProgramArguments</key>
    <array>
        <string>bash</string>
        <string>-c</string>
        <string>cd {install_path} && .venv/bin/python src/arcade_station/core/common/start_pegasus.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
        
        with open(plist_file, "w") as f:
            f.write(plist_content)
            
        self.logger.info("Created macOS launch agent")
    
    def _write_toml(self, file_path: str, data: Dict[str, Any]) -> None:
        """Write a TOML file.
        
        Args:
            file_path: Path to write the file
            data: Data to write
        """
        try:
            # Try to use tomli_w if available
            import tomli_w
            with open(file_path, "wb") as f:
                tomli_w.dump(data, f)
        except ImportError:
            # Fallback to manual TOML writing
            self._write_toml_manually(file_path, data)
    
    def _write_toml_manually(self, file_path: str, data: Dict[str, Any], indent: int = 0) -> None:
        """Write a TOML file manually if tomli_w is not available.
        
        Args:
            file_path: Path to write the file
            data: Data to write
            indent: Current indentation level
        """
        with open(file_path, "w", encoding="utf-8") as f:
            self._write_toml_section(f, data, indent)
    
    def _write_toml_section(self, file, data: Dict[str, Any], indent: int = 0, section_path: str = "") -> None:
        """Write a section of a TOML file.
        
        Args:
            file: File to write to
            data: Data to write
            indent: Current indentation level
            section_path: Current section path for context
        """
        for key, value in data.items():
            if isinstance(value, dict):
                # Write a table header
                current_section = f"{section_path}.{key}" if section_path else key
                file.write(f"[{current_section}]\n")
                self._write_toml_section(file, value, indent + 2, current_section)
                file.write("\n")
            else:
                # Write a key-value pair
                # Check if we're in the key_mappings section and need to quote the key
                if section_path == "key_mappings":
                    # Ensure the key is quoted properly
                    if not (key.startswith('"') and key.endswith('"')):
                        key = f'"{key}"'
                
                if isinstance(value, str):
                    # Convert backslashes to forward slashes for paths
                    if any(path_key in key.lower() for path_key in ['path', 'banner', 'rom', 'state']):
                        value = value.replace('\\', '/')
                    file.write(f'{key} = "{value}"\n')
                elif isinstance(value, bool):
                    file.write(f"{key} = {str(value).lower()}\n")
                else:
                    file.write(f"{key} = {value}\n") 