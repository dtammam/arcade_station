# Arcade Station Installer

arcade station is a front-end interface for managing and interacting with the games you love.
*While the core codebase supports Windows, Linux, and macOS, this MVP release provides a streamlined Windows installation experience. Support for Mac and Linux installers will be available in upcoming releases.*

## Features

- Cross-platform core functionality (Windows, Linux, and macOS)
- Easy-to-use installation wizard (Windows installer in this release)
- Game configuration for ITGMania, binary games, and MAME
- Control device configuration (arcade controls, gamepads, and keyboard)
- Cabinet lighting setup for RGB LED integration
- System utilities and maintenance tools

## Installation

### Quick Start (Windows - Current Release)

1. Download the latest release from the [releases page](https://github.com/yourusername/arcade_station/releases)
2. Extract the downloaded zip file, keeping the top-level `arcade_station` folder intact
3. Run `install_arcade_station.exe`
4. Follow the installation wizard to configure your setup
   - You can rerun the installer later to update settings
5. Once installation is complete, navigate to the installation directory
6. Launch `launch_arcade_station.bat` whenever you want to start Arcade Station

> **Note:** While the core codebase is cross-platform, this initial release focuses on Windows installation. Mac and Linux installers are in development and will be available soon.

### Requirements

The required Python version and libraries are bundled within a contained virtual environment.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

### Third-Party Components

This project incorporates several third-party components. See [NOTICE](NOTICE) for detailed attribution and licensing information.

## Credits
- This guy 👉🏼😉👈🏼
- The current state of generative AI (most specifically, ChatGPT, Cursor, Anthropic's Claude 3.7 with thinking - jesus did that make this possible)
- clue for the original [ddr-picker](https://github.com/evanclue/ddr-picker) which inspired my [PowerShell rewritten fork](https://github.com/dtammam/ddr-picker) and ongoing developments which led to Arcade Station
- also clue for the awesome art assets
- My friend JMK for being a constant source of inspiration
- din and teej for being awesome about sharing ideas, recommendations, feedback for things like ITGmania compatible modules, art, user experience considerations, STAC board firmware and lights reset utilities
- Ashley Philbrick for listening to me ramble about progress on an endless to-do list for the last few months anbd providing encouragement
- Last but not least, Marcy and Daisy for putting up with me programming furiously without knowing what it was about but trusting me when I said it was cool and important