#!/bin/bash
# This is a wrapper script that calls the platform-specific script based on OS detection

# Determine the script location
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Detect operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Detected macOS, using macOS-specific script..."
    bash "$SCRIPT_DIR/src/arcade_station/core/macos/arcade_station_start.sh" "$@"
else
    # Linux/Other Unix
    echo "Detected Linux/Unix, using Linux-specific script..."
    bash "$SCRIPT_DIR/src/arcade_station/core/linux/arcade_station_start.sh" "$@"
fi 