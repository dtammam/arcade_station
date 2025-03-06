# arcade_station
arcade_station is a front-end interface for managing and interacting with the games you love.
![Demo Collage](assets/images/readme/demo-collage.jpg)

## Project Status: Phases 1 & 2 Complete! 🎉

**✅ Phase 1: Core logic and scaffolding in Python**
- Successfully migrated and refactored core functionality to Python
- Recreated all base scripts for critical functions (managing Pegasus, launching games, etc.)
- Implemented keyboard listeners and key bindings for system control

**✅ Phase 2: Cross-platform compatibility**
- Created platform-agnostic solutions for all system dependencies
- Validated functionality across Windows, Linux, and macOS
- Implemented marquee display system that works across all supported platforms

**Coming Next:**
- Phase 3: User-friendly installer creation
- Phase 4: Extended options and customization features

## Motivation
The motivation behind this project is a desire to recreate the [ddr-picker](https://github.com/dtammam/ddr-picker) project from scratch so that the larger rhythm-game community can easily use it for any of their needs. This has been a passion project since I first saw [evan clue's version](https://github.com/evanclue/ddr-picker) - it inspired me to make it my own by refactoring it in PowerShell and by adding tons of new features. Now, I'm off to do it again - by the end, it'll provide the best of the ddr-picker experience while having a seamless install experience for those not technically savvy.

## Installation

**Super user-friendly installer coming soon in Phase 3!**

Stay tuned for our one-click installation solution that will handle all the setup for you.

> **Note:** This application requires Python 3.12.9. If you have multiple Python versions installed, the launcher will attempt to find and use the correct version.

## Features

- Seamless startup experience with automatic dependency management
- Cross-platform support for Windows, Linux, and macOS
- Dynamic marquee display for game banners and artwork
- Configurable key binding system for navigation and control
- Deep integration with Pegasus-FE frontend
- Support for ITGMania dynamic marquee display
- Optional VPN connectivity for networked cabinets
- Windows shell replacement capability
- Process management for optimal game performance
- Platform-specific optimizations and compatibility solutions

## Supported Applications

| Application                                   | Windows | Linux | Mac |
|-----------------------------------------------|---------|-------|-----|
| Pegasus-FE (Frontend interface)               | ✅      | ✅    | ✅  |
| MAME (Arcade emulator)                        | ✅      | ✅    | ✅  |
| ITGMania (Dance game simulator)               | ✅      | ✅    | ✅  |
| Lighting control (Litboard support)           | ✅      | ✅    | ❌  |
| OBS Studio (Streaming/recording)              | ✅      | ✅    | ✅  |
| Screenshot and media management               | ✅      | ✅    | ✅  |

## Integration with ITGMania

Arcade Station can display song banners from ITGMania on your marquee display in real-time as you select them. To set up this integration:

1. Make sure Arcade Station is installed and configured
2. Run the setup script from the arcade_station root directory:
   ```
   python setup_itgmania_dynamic_marquee_for_song_banners.py
   ```
3. Follow the prompts to specify your ITGMania installation path
4. The setup script will automatically:
   - Copy the necessary files to your ITGMania installation
   - Configure Arcade Station to use the dynamic marquee feature
   - Create the required log file in the correct location

Once set up, your marquee display will automatically show the banner for songs you select while playing ITGMania!

## Technical Details

Arcade Station is built with Python 3.12 and follows Google's Python style guidelines. The codebase is designed to be:

- Modular and well-documented
- Cross-platform compatible
- Configuration-driven via TOML files
- Easy to extend and customize

The project uses a virtual environment (`venv`) with explicit dependencies listed in `requirements.txt`.

## Contributing

Contribution guidelines will be published after Phase 4 is complete. If you're interested in contributing before then, please reach out directly.