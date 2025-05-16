@echo off
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

REM Kill all Arcade Station processes
echo Terminating Arcade Station...
"%PYTHON_EXE%" src\arcade_station\core\common\kill_arcade_station.py

echo All Arcade Station processes have been terminated.
pause
exit /b 