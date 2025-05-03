# Arcade Station Installer

A cross-platform installer for the Arcade Station game launcher.

## Features

- Cross-platform support (Windows, Linux, and macOS)
- Graphical user interface with easy-to-follow wizard
- Game configuration for ITGMania, binary games, and MAME
- Control device configuration (arcade controls, gamepads, and keyboard)
- Cabinet lighting setup for RGB LED integration
- System utilities and maintenance tools

## Installation

### From Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/arcade_station.git
cd arcade_station
```

2. Install the package in development mode:
```bash
pip install -e .
```

3. Run the installer:
```bash
arcade-station-installer
```

### Using the Executable

1. Download the latest release from the [releases page](https://github.com/yourusername/arcade_station/releases)
2. Run the executable

## Development

### Requirements

- Python 3.8 or higher
- Tkinter (usually included with Python)
- Pillow (for image processing)

### Building the Executable

To build the executable installer, use PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=arcade_station_installer/installer/resources/icon.ico arcade_station_installer/main.py
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

### Third-Party Components

This project incorporates several third-party components. See [NOTICE](NOTICE) for detailed attribution and licensing information.

## Credits

- Arcade Station Team
- Contributors to the project