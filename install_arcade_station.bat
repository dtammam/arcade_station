@echo off
REM ============================================================================
REM Arcade Station Installer
REM ============================================================================
REM This script serves as the main entry point for installing Arcade Station.
REM It performs the following tasks:
REM 1. Verifies administrator privileges
REM 2. Unblocks all files to prevent Windows security warnings
REM 3. Launches the PowerShell-based installation logic
REM
REM The script requires administrator privileges to:
REM - Modify system settings
REM - Install Python packages
REM - Create virtual environments
REM - Set up file permissions
REM ============================================================================

:: Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This installer requires administrator privileges.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo Running installer with administrator privileges...
echo Unblocking all files - please wait...
powershell -ExecutionPolicy Bypass -Command "Get-ChildItem -Path '%~dp0' -Recurse | Unblock-File"
powershell -ExecutionPolicy Bypass -NoProfile -NonInteractive -File "%~dp0install_logic.ps1"
if %ERRORLEVEL% neq 0 (
    echo Script finished with errors or was cancelled.
    pause
)
exit /b %ERRORLEVEL%