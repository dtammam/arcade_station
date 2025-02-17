import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from arcade_station.core.common.core_functions import *

kill_processes_from_toml('processes_to_kill.toml')