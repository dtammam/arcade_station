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

:: Find the best Python version for creating virtual environment
set PYTHON_CMD=python
set PYTHON_VERSION_FOUND=false

:: Try to find Python 3.12.9 via Python launcher
where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    for /f "delims=" %%i in ('py -3.12 -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}')" 2^>nul') do (
        if "%%i"=="3.12.9" (
            set PYTHON_CMD=py -3.12
            set PYTHON_VERSION_FOUND=true
            echo Found Python 3.12.9 via Python Launcher for creating virtual environment.
        )
    )
)

:: Try other ways to find Python if not found yet
if "%PYTHON_VERSION_FOUND%"=="false" (
    where python3.12 >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        for /f "delims=" %%i in ('python3.12 -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}')" 2^>nul') do (
            if "%%i"=="3.12.9" (
                set PYTHON_CMD=python3.12
                set PYTHON_VERSION_FOUND=true
                echo Found Python 3.12.9 via python3.12 command.
            )
        )
    )
)

:: Last resort: check standard python command
if "%PYTHON_VERSION_FOUND%"=="false" (
    where python >nul 2>nul
    if %ERRORLEVEL% neq 0 (
        echo Python is not installed or not in PATH.
        echo Please install Python 3.12.9.
        pause
        exit /b 1
    )

    :: Check Python version
    for /f "delims=" %%i in ('python -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}')"') do set PYTHON_VERSION=%%i
    echo Detected Python version: %PYTHON_VERSION%

    :: Warn if not using ideal version
    if "%PYTHON_VERSION%" neq "3.12.9" (
        echo Warning: This application was developed with Python 3.12.9.
        echo Current Python version: %PYTHON_VERSION% will be used to create virtual environment.
        echo Some features may not work correctly.
        echo.
        choice /C YN /M "Continue with Python %PYTHON_VERSION%?"
        if !ERRORLEVEL! equ 2 (
            echo Exiting.
            exit /b 1
        )
        echo.
    ) else (
        echo Using default Python 3.12.9 for virtual environment.
    )
)

:: Set up or verify the virtual environment
echo.
echo Setting up Python virtual environment...

:: Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating one...
    %PYTHON_CMD% -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
    
    echo Installing requirements in virtual environment...
    call .venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo Failed to install requirements.
        pause
        exit /b 1
    )
) else (
    echo Using existing virtual environment...
    
    :: Activate and check packages
    call .venv\Scripts\activate.bat
    
    :: Check if psutil is installed in the virtual environment
    python -c "import pkgutil; exit(0 if pkgutil.find_loader('psutil') else 1)" >nul 2>nul
    if %ERRORLEVEL% neq 0 (
        echo Required packages missing in virtual environment. Reinstalling...
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        if %ERRORLEVEL% neq 0 (
            echo Failed to install requirements.
            pause
            exit /b 1
        )
    )
)

:: Virtual environment should be activated
call .venv\Scripts\activate.bat

:: Set PYTHONPATH to include the project root
set "PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%"

:: Run the startup script with the activated virtual environment
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