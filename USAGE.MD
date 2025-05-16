# Usage Guide

This guide provides detailed information on how to use Arcade Station, from installation to advanced configuration.

## Installer Walkthrough

The Arcade Station installer is designed to be straightforward and guide you through the necessary setup steps. Here's an overview of what each page in the installer does:

### 1. Welcome Page
This is the first screen you'll see. It provides a brief introduction to Arcade Station and outlines the installation process. Click "Next" to proceed.

### 2. Installation Directory
On this page, you'll choose where Arcade Station will be installed on your system.
- **Default Location**: A default path is suggested, but you can browse and select a different directory if needed.
- **Disk Space**: Ensure the selected drive has enough free space (approximately 500MB).
Click "Next" after selecting your desired installation path.

### 3. Game Configuration
This section allows you to configure paths for your games and emulators. Depending on what you plan to use, you might see several sub-sections:

#### ITGMania Setup
- **ITGMania Path**: Specify the main installation folder for ITGMania.
- **Song Packs**: If applicable, you might be asked to point to your song pack directories.

#### MAME Setup
- **MAME Executable**: Provide the path to your MAME executable file (e.g., `CL\games\mame.exe`).
- **ROMs Directory**: Specify the folder where your MAME ROMs are stored.

### 4. Dependency Configuration (Windows Only)
Certain features rely on third-party tools. This page helps configure them:
- **AudioSwitcher**: If you plan to use AudioSwitcher for volume OSD when `explorer.exe` is not the shell, ensure it's installed and the installer can locate it, or configure its path here.
- **Litboard Support**: For users with lit arcade dance pads, this step might involve configuring paths to `mame2lit.exe` or `LightsTest.exe`.

### 5. Summary
Before the actual installation begins, this page will display a summary of all the choices you've made (installation directory, game paths, etc.). Review these settings carefully. If anything needs to be changed, you can go "Back" to previous pages.
Once you're satisfied, click "Install" to begin copying files and setting up Arcade Station.

### 6. Installation Progress
This page shows the progress of the installation. Wait for it to complete.

### 7. Completion
Once the installation is finished, you'll see a completion screen. It may provide options such as:
- Launching Arcade Station immediately.
- Opening the installation folder.
- Viewing this Usage Guide.

Click "Finish" to exit the installer.

## Post-Installation
After a successful installation, navigate to the directory where you installed Arcade Station. You can start the application by running `launch_arcade_station.bat`.

For re-configuration, you can run `install_arcade_station.bat` again and point it to your existing installation directory.

---

*More sections on advanced usage, troubleshooting, and customization will be added here in the future.* 