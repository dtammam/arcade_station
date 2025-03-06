#!/bin/bash
# Run the Python script in the background to prevent terminal windows
# Assumes the virtual environment is in the standard location

# Get the absolute path to the repository
REPO_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Run the script using pythonw if available (macOS) or nohup (Linux)
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS - use pythonw which doesn't show a console
  "$REPO_PATH/.venv/bin/pythonw" "$REPO_PATH/src/arcade_station/screenshot.py" &
else
  # Linux - use nohup to prevent terminal output
  nohup "$REPO_PATH/.venv/bin/python" "$REPO_PATH/src/arcade_station/screenshot.py" > /dev/null 2>&1 &
fi 