"""
This module contains all the pages for the Arcade Station Installer UI.
"""
from .base_page import BasePage
from .welcome_page import WelcomePage
from .install_location_page import InstallLocationPage
from .kiosk_mode_page import KioskModePage
from .display_config_page import DisplayConfigPage
from .game_setup_page import GameSetupPage
from .itgmania_setup_page import ITGManiaSetupPage
from .binary_games_page import BinaryGamesPage
from .mame_games_page import MAMEGamesPage
from .key_bindings_page import KeyBindingsPage
from .utility_config_page import UtilityConfigPage
from .summary_page import SummaryPage

__all__ = [
    'BasePage',
    'WelcomePage',
    'InstallLocationPage',
    'KioskModePage',
    'DisplayConfigPage',
    'GameSetupPage',
    'ITGManiaSetupPage',
    'BinaryGamesPage',
    'MAMEGamesPage',
    'KeyBindingsPage',
    'UtilityConfigPage',
    'SummaryPage',
] 