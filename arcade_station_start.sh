#!/bin/bash
# This is a wrapper script that calls the platform-specific script based on OS detection

# Determine the script location
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check for Python 3.12.9
check_python() {
    if command -v python3.12 &>/dev/null; then
        python_version=$(python3.12 -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}')")
        if [ "$python_version" = "3.12.9" ]; then
            echo "Found Python 3.12.9!"
            return 0
        fi
    fi
    return 1
}

# Install Python 3.12.9 on macOS
install_python_macos() {
    echo "Python 3.12.9 not found. Would you like to install it? (y/n)"
    read -r install_python
    if [[ "$install_python" =~ ^[Yy]$ ]]; then
        echo "Installing Python 3.12.9 on macOS..."
        
        # Check if Homebrew is installed
        if ! command -v brew &>/dev/null; then
            echo "Homebrew not found. Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            if [ $? -ne 0 ]; then
                echo "Failed to install Homebrew. Please install manually."
                return 1
            fi
        fi
        
        # Install Python 3.12.9 with Homebrew
        brew update
        brew install python@3.12
        
        if [ $? -ne 0 ]; then
            echo "Failed to install Python 3.12. Please install manually."
            return 1
        fi
        
        # Check if Python 3.12.9 is installed
        if ! check_python; then
            echo "Python 3.12.9 installation verification failed."
            return 1
        fi
        
        echo "Python 3.12.9 installed successfully!"
        return 0
    else
        echo "Python installation skipped."
        return 1
    fi
}

# Install Python 3.12.9 on Linux
install_python_linux() {
    echo "Python 3.12.9 not found. Would you like to install it? (y/n)"
    read -r install_python
    if [[ "$install_python" =~ ^[Yy]$ ]]; then
        echo "Installing Python 3.12.9 on Linux..."
        
        # Create temp directory
        mkdir -p "$SCRIPT_DIR/temp"
        cd "$SCRIPT_DIR/temp"
        
        # Determine package manager and install dependencies
        if command -v apt-get &>/dev/null; then
            echo "Debian/Ubuntu detected. Installing dependencies..."
            sudo apt-get update
            sudo apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev curl
        elif command -v dnf &>/dev/null; then
            echo "Fedora/RHEL detected. Installing dependencies..."
            sudo dnf groupinstall "Development Tools" -y
            sudo dnf install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel libpcap-devel xz-devel libffi-devel -y
        elif command -v pacman &>/dev/null; then
            echo "Arch Linux detected. Installing dependencies..."
            sudo pacman -S --needed base-devel openssl zlib
        else
            echo "Unsupported Linux distribution. Please install Python 3.12.9 manually."
            return 1
        fi
        
        # Download and extract Python 3.12.9
        echo "Downloading Python 3.12.9 source..."
        curl -O https://www.python.org/ftp/python/3.12.9/Python-3.12.9.tgz
        if [ $? -ne 0 ]; then
            echo "Failed to download Python 3.12.9 source. Please install manually."
            return 1
        fi
        
        tar -xzf Python-3.12.9.tgz
        cd Python-3.12.9
        
        # Configure and compile Python
        echo "Configuring and compiling Python 3.12.9..."
        ./configure --enable-optimizations --with-ensurepip=install
        make -j $(nproc)
        
        # Install Python
        echo "Installing Python 3.12.9..."
        sudo make altinstall
        
        if [ $? -ne 0 ]; then
            echo "Failed to install Python 3.12.9. Please install manually."
            return 1
        fi
        
        # Create symbolic links if not exist
        if ! command -v python3.12 &>/dev/null; then
            sudo ln -sf /usr/local/bin/python3.12 /usr/local/bin/python3.12
        fi
        
        # Check if Python 3.12.9 is installed
        cd "$SCRIPT_DIR"
        if ! check_python; then
            echo "Python 3.12.9 installation verification failed."
            return 1
        fi
        
        # Clean up
        rm -rf "$SCRIPT_DIR/temp"
        
        echo "Python 3.12.9 installed successfully!"
        return 0
    else
        echo "Python installation skipped."
        return 1
    fi
}

# Detect operating system and check/install Python
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Detected macOS..."
    if check_python; then
        echo "Using Python 3.12.9 for Arcade Station..."
        # Continue with macOS script
        bash "$SCRIPT_DIR/src/arcade_station/core/macos/arcade_station_start.sh" "$@"
    else
        # Try to install Python
        if install_python_macos; then
            echo "Using the newly installed Python 3.12.9 for Arcade Station..."
            bash "$SCRIPT_DIR/src/arcade_station/core/macos/arcade_station_start.sh" "$@"
        else
            echo "Falling back to macOS-specific script..."
            bash "$SCRIPT_DIR/src/arcade_station/core/macos/arcade_station_start.sh" "$@"
        fi
    fi
else
    # Linux/Other Unix
    echo "Detected Linux/Unix..."
    if check_python; then
        echo "Using Python 3.12.9 for Arcade Station..."
        # Continue with Linux script
        bash "$SCRIPT_DIR/src/arcade_station/core/linux/arcade_station_start.sh" "$@"
    else
        # Try to install Python
        if install_python_linux; then
            echo "Using the newly installed Python 3.12.9 for Arcade Station..."
            bash "$SCRIPT_DIR/src/arcade_station/core/linux/arcade_station_start.sh" "$@"
        else
            echo "Falling back to Linux-specific script..."
            bash "$SCRIPT_DIR/src/arcade_station/core/linux/arcade_station_start.sh" "$@"
        fi
    fi
fi 