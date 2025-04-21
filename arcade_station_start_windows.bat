@echo off
REM This is a wrapper script that calls the platform-specific script

echo Arcade Station Launcher
echo ----------------------
echo.

set "SCRIPT_DIR=%~dp0"
cd "%SCRIPT_DIR%"

echo Finding best Python installation for virtual environment...

REM Check if py launcher exists and try to find Python 3.12.9
where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    for /f "delims=" %%i in ('py -3.12 -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}')" 2^>nul') do (
        if "%%i"=="3.12.9" (
            echo Found Python 3.12.9! Using it to create/update virtual environment...
            goto setupVenv
        )
    )
)

echo Python 3.12.9 not found. Would you like to install it? (Y/N)
set /p INSTALL_PYTHON=
if /i "%INSTALL_PYTHON%"=="Y" (
    echo Downloading Python 3.12.9 installer...
    
    REM Create temp directory if it doesn't exist
    if not exist "%SCRIPT_DIR%\temp" mkdir "%SCRIPT_DIR%\temp"
    
    REM Download Python installer
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe' -OutFile '%SCRIPT_DIR%\temp\python-3.12.9-amd64.exe'}"
    
    if %ERRORLEVEL% neq 0 (
        echo Failed to download Python installer.
        echo Please install Python 3.12.9 manually from https://www.python.org/downloads/
        echo Falling back to platform-specific script...
        goto useDefaultScript
    )
    
    echo Installing Python 3.12.9...
    echo This may take a few minutes. Please wait...
    
    REM Install Python silently with pip and add to PATH
    "%SCRIPT_DIR%\temp\python-3.12.9-amd64.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1 Include_launcher=1
    
    if %ERRORLEVEL% neq 0 (
        echo Failed to install Python 3.12.9.
        echo Falling back to platform-specific script...
        goto useDefaultScript
    )
    
    echo Python 3.12.9 installed successfully!
    echo Refreshing environment variables...
    
    REM Refresh environment variables without relying on refreshenv.cmd
    powershell -Command "& {$env:Path = [System.Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path', 'User')}"
    
    REM Verify Python installation
    echo Verifying Python installation...
    py -3.12 --version >nul 2>nul
    if %ERRORLEVEL% neq 0 (
        echo Python installation verification failed.
        echo Python was installed but may not be in your PATH.
        echo Please restart your computer and try again.
        exit /b
    )
    
    echo Python 3.12.9 is now installed and ready to use!
) else (
    echo Python installation skipped.
    echo Falling back to platform-specific script...
    goto useDefaultScript
)

:setupVenv
REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Creating virtual environment with Python 3.12.9...
    py -3.12 -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo Failed to create virtual environment.
        echo Falling back to platform-specific script...
        goto useDefaultScript
    )
)

REM Activate virtual environment and ensure packages are installed
call .venv\Scripts\activate.bat
python -c "import pkgutil; exit(0 if pkgutil.find_loader('psutil') else 1)" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installing required packages in virtual environment...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo Failed to install requirements.
        echo Falling back to platform-specific script...
        goto useDefaultScript
    )
)

echo Starting Arcade Station with virtual environment...
echo.

REM Run the standard startup script
python src\arcade_station\start_frontend_apps.py %*

REM Check if Pegasus started successfully by looking for its process
echo Checking if Pegasus started successfully...
timeout /t 5 /nobreak >nul
python -c "import psutil; print(any('pegasus-fe' in p.name().lower() for p in psutil.process_iter()))" > "%TEMP%\pegasus_check.txt"
set /p PEGASUS_RUNNING=<"%TEMP%\pegasus_check.txt"
del "%TEMP%\pegasus_check.txt"

if not "%PEGASUS_RUNNING%"=="True" (
    echo.
    echo WARNING: Pegasus does not appear to be running!
    echo Running diagnostic tool to troubleshoot...
    echo.
    python src\arcade_station\debug_pegasus_launch.py --create-launcher
    echo.
    echo If Pegasus still fails to start, you can:
    echo 1. Run the diagnostic script manually with: python src\arcade_station\debug_pegasus_launch.py
    echo 2. Use the direct launcher script created in the src\arcade_station directory
    echo 3. Check the logs for more information
    echo.
)

exit /b

:useDefaultScript
REM Call the platform-specific script as a fallback
echo Using platform-specific script to setup environment...
echo.
call src\arcade_station\core\windows\arcade_station_start.bat %* 