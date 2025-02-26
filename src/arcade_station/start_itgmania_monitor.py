"""
Launch the ITGMania monitor to display song banners on the marquee.
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