import sys
import os
# Add the parent directory to the Python path to allow relative module imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from core.core_functions import *

kill_processes_from_toml('processes_to_kill.toml')
start_pegasus()