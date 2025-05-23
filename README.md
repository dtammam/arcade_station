# Arcade Station

[![Python Version](https://img.shields.io/badge/python-3.12.9-blue.svg)](https://www.python.org/downloads/release/python-3129/)
[![License](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

<div align="center">
   <img src="assets/images/readme/logo.png" width="300" alt="Logo"/>
</div>

<h2 align="center">Arcade Station is a front-end interface for managing and interacting with the games you love.</h2>

<div align="center">
   <img src="assets/images/readme/collage.png" width="900" alt="Collage"/>
</div>

## Table of Contents
- [✨ Features](#features)
- [📋 Requirements](#requirements)
- [💾 Installation](#installation)
- [🎮 Example Setup](#example-setup)
- [🐛 Known Issues](#known-issues)
- [⚖️ License](#license)
- [🙏 Acknowledgments](#acknowledgments)

## ✨ Features

- Cross-platform core functionality (Windows, Linux, and macOS)
- Easy-to-use installation wizard (Windows installer in this release)
- Game configuration for ITGMania, binary games, and MAME

## 📋 Requirements

### 💻 Technical
- [Python 3.12.9](https://www.python.org/downloads/release/python-3129/)
- Windows 10/11 (current release)
- Administrator privileges for installation
- 500MB free disk space

### 🔒 UAC
Arcade Station is designed primarily for private, arcade-style machines running in a kiosk-like environment.

While scripts may function with User Access Control (UAC) enabled, the full experience (including shell replacement and seamless startup) only works reliably with UAC disabled. In standard desktop setups, functionality may be partial or inconsistent. We recommend:

- UAC disabled (Never notify)
- Autologin with the local user
- Trusted software only
- No general-purpose use
- Physical access limited to trusted users

This configuration ensures the system behaves as intended and delivers a smooth, arcade-style experience.
This recommendation is based on practical needs for stability and predictability in arcade-style deployments. Use at your discretion.

## 💾 Installation

### ℹ️ Platform Support
**Note:** While the core codebase is cross-platform, this initial release focuses on Windows installation. Mac and Linux installers are in development and will be available soon.

### 🪟 (Windows - Current Release)

1. Download and install [Python 3.12.9](https://www.python.org/downloads/release/python-3129/). *You must select install as Admin and add to PATH options!*

   <img src="assets/images/readme/python.png" width="500" alt="Python options" />

2. If intending on using this with kiosk mode, disable UAC. 
3. Download Arcade Station by cloning the repo or by clicking `Code/Download ZIP`

   <img src="assets/images/readme/download.png" width="500" alt="Download ZIP" />

4. Right-click and run `install_arcade_station.bat` from the cloned repo/extracted .zip as Administrator. If warned about Windows protecting your PC, select more options and `Run anyway`.

   <img src="assets/images/readme/warning.png" width="500" alt="Security warning" />

5. Go through the setup, starting by choosing where you'd want the program installed. For additional information, please see the [USAGE](USAGE.md) guide.


6. Once installation is complete, the location you installed arcade station in will open in Windows Explorer.

7. Run `launch_arcade_station.bat`. The launcher will automatically unblock all files to prevent security warnings.

   <img src="assets/images/readme/warning.png" width="500" alt="Security warning" />

Congrats, you're setup! Whenever you want to start Arcade Station. Re-run `install_arcade_station.bat` and point to your install directory to reconfigure it.

## 🎮 Example Setup

For a detailed walkthrough with examples showing the complete installation and usage flow, check out our [LAPTOP](examples/LAPTOP.md) guide. This demonstration shows how to set up Arcade Station on a laptop with external monitors, configuring games like ITGmania and Megatouch Maxx, and using the dynamic marquee feature.

## 🐛 Known Issues

- When reconfiguring an existing installation, there may be a blank game field when selecting binary games. You must delete this field before adding a new game.
- When selecting utilities, the default ..\..\ lights programs will not resolve correctly. They will be removed and the browse button will be made visible shortly.

These issues are being actively investigated and will be fixed in an upcoming update.

## ⚖️ License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
This project incorporates several third-party components. See [NOTICE](NOTICE) for detailed attribution and licensing information.

## 🙏 Acknowledgments

Please reference the [THANKS](THANKS.md) file.