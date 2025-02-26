@echo off
setlocal enabledelayedexpansion

:: Determine the project root directory
set "SCRIPT_DIR=%~dp0"
cd "%SCRIPT_DIR%\..\..\..\..\"
set "PROJECT_ROOT=%cd%"

:: Check if we're running as a shell replacement
set SHELL_MODE=false
if "%1"=="--shell" (
    set SHELL_MODE=true
    echo Running in shell replacement mode...
)

:: Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.12.8.
    pause
    exit /b 1
)

:: Check Python version
for /f "tokens=2" %%i in ('python -c "import sys; print(sys.version.split()[0])"') do set PYTHON_VERSION=%%i
echo Detected Python version: %PYTHON_VERSION%

if "%PYTHON_VERSION%" neq "3.12.8" (
    echo Warning: This application was developed with Python 3.12.8.
    echo Current version: %PYTHON_VERSION%
    echo Some features may not work correctly.
    echo.
    choice /C YN /M "Continue anyway?"
    if !ERRORLEVEL! equ 2 (
        echo Exiting due to Python version mismatch.
        exit /b 1
    )
    echo.
)

:: Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating one...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
    
    echo Installing requirements...
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo Failed to install requirements.
        pause
        exit /b 1
    )
) else (
    echo Using existing virtual environment...
)

:: Activate the virtual environment
call .venv\Scripts\activate.bat

:: Set PYTHONPATH to include the project root
set "PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%"

:: Run the startup script with or without shell mode
if "%SHELL_MODE%"=="true" (
    python "%PROJECT_ROOT%\src\arcade_station\start_frontend_apps.py" --shell-mode
) else (
    python "%PROJECT_ROOT%\src\arcade_station\start_frontend_apps.py"
)

:: Only pause if not in shell mode
if "%SHELL_MODE%"=="false" (
    pause
)

endlocal 