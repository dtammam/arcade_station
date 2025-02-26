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
            python src\arcade_station\start_frontend_apps.py %*
            exit /b
        )
    )
)

:useDefaultScript
REM Call the platform-specific script as a fallback
echo Using platform-specific script to setup environment...
echo.
call src\arcade_station\core\windows\arcade_station_start.bat %* 