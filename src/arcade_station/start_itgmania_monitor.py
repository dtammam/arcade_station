"""
ITGMania Monitor Launcher for Arcade Station.

This script serves as the entry point for launching the ITGMania monitor service,
which displays song banners on the marquee display. It:
1. Sets up the Python path for proper module imports
2. Initializes the ITGMania log monitoring system
3. Handles song banner display updates in real-time

The monitor watches the ITGMania log file for changes and updates the marquee
display accordingly, providing dynamic visual feedback during gameplay.
"""

import sys
import os

# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from arcade_station.launchers.monitor_itgmania import monitor_itgmania_log
from arcade_station.core.common.core_functions import log_message

if __name__ == "__main__":
    log_message("Starting ITGMania monitor", "BANNER")
    monitor_itgmania_log() 