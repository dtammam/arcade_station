# Arcade Station

[![Python Version](https://img.shields.io/badge/python-3.12.9-blue.svg)](https://www.python.org/downloads/release/python-3129/)
[![License](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

<p align="center"><img src="assets/images/readme/logo.png" width="300" alt="Logo" /></p>

<h2 align="center">Arcade Station is a front-end interface for managing and interacting with the games you love.</h2>

<p align="center"><img src="assets/images/readme/collage.png" width="900" alt="Logo" /></p>

## Table of Contents
- [✨ Features](#features)
- [💾 Installation](#installation)
- [📋 Requirements](#requirements)
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

While scripts may function with UAC enabled, the full experience - including shell replacement and seamless startup - only works reliably with UAC disabled. In standard desktop setups, functionality may be partial or inconsistent. We recommend:

- UAC disabled
- Autologin with the local user
- Trusted software only
- No general-purpose use
- Physical access limited to trusted users

This configuration ensures the system behaves as intended and delivers a smooth, arcade-style experience.
This recommendation is based on practical needs for stability and predictability in arcade-style deployments. Use at your discretion.

## 💾 Installation

### 🪟 (Windows - Current Release)

1. Download and install [Python 3.12.9](https://www.python.org/downloads/release/python-3129/). *You must select install as Admin and add to PATH options!*

   <img src="assets/images/readme/python.png" width="500" alt="Python options" />

2. If intending on using this with kiosk mode, disable UAC. 
3. Download Arcade Station by cloning the repo or by clicking `Code/Download ZIP`

   <img src="assets/images/readme/download.png" width="500" alt="Download ZIP" />

4. Right-click and run `install_arcade_station.bat` from the cloned repo/extracted .zip as Administrator. If warned about Windows protecting your PC, select more options and `Run anyway`.

   <img src="assets/images/readme/warning.png" width="500" alt="Security warning" />

5. Follow the installation wizard to configure your setup, choosing the desired install location.

6. Once installation is complete, the location you installed arcade station in will open in Windows Explorer.

7. Run `launch_arcade_station.bat`. If warned about Windows protecting your PC, select more options and `Run anyway`.

   <img src="assets/images/readme/warning.png" width="500" alt="Security warning" />

Congrats, you're setup! Whenever you want to start Arcade Station. Re-run `install_arcade_station.bat` and point to your install directory to reconfigure it.

## ⚖️ License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

### Third-Party Components

This project incorporates several third-party components. See [NOTICE](NOTICE) for detailed attribution and licensing information.

## 🙏 Acknowledgments

Please reference the [THANKS](THANKS.md) file.

---

**Note:** While the core codebase is cross-platform, this initial release focuses on Windows installation. Mac and Linux installers are in development and will be available soon.