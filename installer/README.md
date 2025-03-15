# Arcade Station Installer

This is the installer for Arcade Station, a front-end interface for managing and interacting with your favorite games.

## Overview

The Arcade Station Installer provides a modern, user-friendly wizard interface to set up and configure Arcade Station on your system. It handles:

- First-time installation with a complete setup wizard
- Configuration updates for existing installations
- Cross-platform support for Windows, macOS, and Linux

## Features

- Modern UI with customtkinter or standard tkinter fallback
- Cross-platform compatibility
- Automatic detection of existing installations
- Configuration of all Arcade Station features:
  - Dynamic marquee
  - ITGMania integration
  - Game management
  - Key bindings
  - Utility features (lights, VPN, streaming)
  - Windows kiosk mode

## Requirements

- Python 3.12.9
- Dependencies listed in requirements.txt

## Installation

### Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/arcade_station.git
   cd arcade_station/installer
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   # For Windows
   .\.venv\Scripts\activate
   # For macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Installer

From the development environment:

```bash
python -m src.__main__
```

### Building the Standalone Installer

To build a standalone executable:

```bash
pyinstaller --onefile --noconsole --icon=assets/images/arcade_station_icon.ico --add-data="assets/*:assets" --name="ArcadeStationInstaller" src/__main__.py
```

This will create an executable in the `dist` directory.

## Development

### Project Structure

```
installer/
├── requirements.txt
├── README.md
├── src/
│   ├── __main__.py           # Entry point
│   ├── core/                 # Core functionality
│   │   └── core_functions.py 
│   ├── wizard/               # Wizard framework
│   │   ├── base_wizard.py    # Base wizard classes
│   │   ├── initial_wizard.py # First-time installation wizard
│   │   ├── update_wizard.py  # Update wizard
│   │   └── pages/            # UI pages
│   ├── configurators/        # Configuration managers
│   │   ├── toml_manager.py   # TOML file manager
│   │   ├── pegasus_manager.py # Pegasus metadata manager
│   │   └── os_specific/      # OS-specific configuration
│   └── utils/                # Utility functions
```

### Adding Pages

1. Create a new page class in `src/wizard/pages/`
2. Inherit from `BasePage` in `base_wizard.py`
3. Implement `setup_ui()`, `validate()`, and `apply()` methods
4. Register the page in the appropriate wizard class

Example:

```python
from wizard.base_wizard import BasePage

class MyNewPage(BasePage):
    def setup_ui(self):
        # Create UI elements
        pass
        
    def validate(self):
        # Validate user input
        return True
        
    def apply(self):
        # Store data in wizard.config_data
        self.wizard.set_config('my_section', {'key': 'value'})
```

### Coding Standards

- Follow PEP 8 style guidelines
- Use Google-style docstrings
- Maximum line length of 79 characters
- Ensure cross-platform compatibility
- Handle all exceptions appropriately

## License

[Specify the license] 
