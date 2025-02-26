# arcade_station
arcade_station is a front-end interface for managing and interacting with the games you love.
![Demo Collage](assets/images/readme/demo-collage.jpg)

## Motivation
The motivation behind this project is a desire to recreate the [ddr-picker](https://github.com/dtammam/ddr-picker) project from scratch so that the larger rhythm-game community can easily use it for any of their needs. This has been a passion project since I first saw [evan clue's version](https://github.com/evanclue/ddr-picker) - it inspired me to make it my own by refactoring it in PowerShell and by adding tons of new features. Now, I'm off to do it again - by the end, it'll provide the best of the ddr-picker experience while having a seamless install experience for those not technically savvy.

## Installation

**Super user-friendly installer coming soon!**

Stay tuned for our one-click installation solution that will handle all the setup for you.

> **Note:** This application requires Python 3.12.9. If you have multiple Python versions installed, the launcher will attempt to find and use the correct version.

## Features

- Seamless startup experience with automatic dependency management
- Cross-platform support (Windows, Linux, macOS)
- Marquee display for game banners
- Key binding system for navigation and control
- Integration with game frontends like Pegasus-FE
- Support for ITGMania dynamic marquee display
- Optional VPN connectivity
- Windows shell replacement capability

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