@echo off
REM ============================================================================
REM Arcade Station Process Terminator
REM ============================================================================
REM This script safely terminates all Arcade Station processes and services.
REM It performs the following tasks:
REM 1. Verifies administrator privileges
REM 2. Sets up the Python environment
REM 3. Terminates all Arcade Station processes
REM 4. Handles both module-style and direct script execution
REM
REM The script requires administrator privileges to:
REM - Terminate system processes
REM - Access virtual environment
REM - Modify system state
REM ============================================================================

REM Check for admin privileges and elevate if needed
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

REM Set PowerShell execution policy to Bypass for this session
powershell -Command "Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force"

REM Arcade Station Kill Script

echo Arcade Station Kill Script
echo -----------------------
echo.

REM Set script working directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Activate the virtual environment
call "%SCRIPT_DIR%.venv\Scripts\activate.bat"

REM Set path to Python executable in the bundled virtual environment
set "PYTHON_EXE=%SCRIPT_DIR%.venv\Scripts\python.exe"

REM Check if Python executable exists
if not exist "%PYTHON_EXE%" (
    echo ERROR: Python virtual environment not found at .venv\Scripts\python.exe
    echo Please ensure the virtual environment is properly set up.
    exit /b 1
)

REM Setup Python path to help find modules
set "PYTHONPATH=%SCRIPT_DIR%;%SCRIPT_DIR%src;%PYTHONPATH%"

REM Kill all Arcade Station processes
echo Terminating Arcade Station...
"%PYTHON_EXE%" -m arcade_station.core.common.kill_arcade_station 2>nul

REM If the module-style import failed, try direct path
if %errorLevel% neq 0 (
    echo Trying alternate method...
    "%PYTHON_EXE%" "%SCRIPT_DIR%src\arcade_station\core\common\kill_arcade_station.py"
)

echo All Arcade Station processes have been terminated.
pause
exit /b 