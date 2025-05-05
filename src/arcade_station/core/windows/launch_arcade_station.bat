@echo off
REM Arcade Station Launcher

echo Arcade Station Launcher
echo ----------------------
echo.

REM Set script working directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Set path to Python executable in the bundled virtual environment
set "PYTHON_EXE=%SCRIPT_DIR%.venv\Scripts\python.exe"

REM Check if Python executable exists
if not exist "%PYTHON_EXE%" (
    echo ERROR: Python virtual environment not found at .venv\Scripts\python.exe
    echo Please ensure the virtual environment is properly set up.
    exit /b 1
)

REM Run the launcher
echo Launching Arcade Station...
"%PYTHON_EXE%" src\arcade_station\start_frontend_apps.py %*

exit /b
