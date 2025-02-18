import sys
import os
import psutil

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from arcade_station.core.common.core_functions import kill_pegasus

# Function to kill Pegasus process
kill_pegasus()