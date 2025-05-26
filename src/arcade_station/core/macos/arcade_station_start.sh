#!/bin/bash

# Arcade Station macOS Startup Script
#
# This script handles the initialization and startup of Arcade Station on macOS systems.
# It performs the following tasks:
# 1. Environment setup and path resolution
# 2. Python version verification (requires 3.12.9)
# 3. Virtual environment management
# 4. Dependencies installation
# 5. Application startup with optional shell mode
#
# Usage:
#   ./arcade_station_start.sh        # Normal startup
#   ./arcade_station_start.sh --shell # Shell replacement mode
#
# Note: This script is designed for macOS and may require additional
# permissions for certain operations (e.g., screen capture, audio).

# Determine the script location and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../../../.." && pwd )"
cd "$PROJECT_ROOT"

# Check if we're running as a shell replacement
SHELL_MODE=false
if [ "$1" == "--shell" ]; then
    SHELL_MODE=true
    echo "Running in shell replacement mode..."
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in PATH."
    echo "Please install Python 3.12.9."
    read -p "Press Enter to continue..."
    exit 1
fi

# Check Python version using a more reliable method
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}')")
echo "Detected Python version: $PYTHON_VERSION"

if [ "$PYTHON_VERSION" != "3.12.9" ]; then
    echo "Warning: This application was developed with Python 3.12.9."
    echo "Current version: $PYTHON_VERSION"
    echo "Some features may not work correctly."
    echo
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting due to Python version mismatch."
        exit 1
    fi
    echo
fi

# Determine the virtual environment path
VENV_ACTIVATE="$PROJECT_ROOT/.venv/bin/activate"

# Check if virtual environment exists
if [ ! -f "$VENV_ACTIVATE" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        read -p "Press Enter to continue..."
        exit 1
    fi
    
    echo "Installing requirements..."
    source "$VENV_ACTIVATE"
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install requirements."
        read -p "Press Enter to continue..."
        exit 1
    fi
else
    echo "Using existing virtual environment..."
fi

# Activate the virtual environment
source "$VENV_ACTIVATE"

# Set PYTHONPATH to include the project root
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Run the startup script with or without shell mode
if [ "$SHELL_MODE" = true ]; then
    python3 "$PROJECT_ROOT/src/arcade_station/start_frontend_apps.py" --shell-mode
else
    python3 "$PROJECT_ROOT/src/arcade_station/start_frontend_apps.py"
fi

# Only pause if not in shell mode
if [ "$SHELL_MODE" = false ]; then
    read -p "Press Enter to continue..."
fi 