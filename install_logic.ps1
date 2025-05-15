#Requires -Version 5.1

# Set strict mode and error action
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Setup logging
$LogDir = Join-Path -Path $PSScriptRoot -ChildPath "install\logs"
if (-not (Test-Path -Path $LogDir)) {
    New-Item -Path $LogDir -ItemType Directory -Force | Out-Null
}
$DateStamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path -Path $LogDir -ChildPath "arcade_station_installer_$DateStamp.log"

function Write-Log {
    param (
        [string]$Message,
        [string]$Color = "White",
        [switch]$NoConsole
    )
    
    $TimeStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$TimeStamp] $Message"
    
    # Always write to log file
    Add-Content -Path $LogFile -Value $LogMessage
    
    # Write to console if not suppressed
    if (-not $NoConsole) {
        Write-Host $Message -ForegroundColor $Color
    }
}

Write-Log "== Arcade Station Setup ==" -Color Cyan
Write-Log "Log file: $LogFile" -Color Gray
Write-Log ""
Write-Log "Verifying Python 3.12 installation..." -Color White

# Check for Python 3.12 using Get-Command (more reliable than just running py)
$Python312Info = Get-Command py -ErrorAction SilentlyContinue
if (-not $Python312Info) {
    Write-Log "ERROR: The 'py' command (Python Launcher) was not found." -Color Red
    Write-Log "Please install Python 3.12 (recommend 3.12.9) from python.org" -Color Yellow
    Write-Log "Ensure it was added to your system PATH during installation." -Color Yellow
    exit 1
}

# Try running the version check
try {
    py -3.12 -V *> $null # Redirect stdout and stderr to null
    if ($LASTEXITCODE -ne 0) { throw "py -3.12 command failed." }
    Write-Log "Found compatible Python 3.12." -Color Green
} catch {
    Write-Log "ERROR: Python 3.12 was not found or failed using the 'py -3.12' command." -Color Red
    Write-Log "Ensure Python 3.12 (recommend 3.12.9) is installed and accessible via 'py -3.12'." -Color Yellow
    Write-Log "Error details: $($_.Exception.Message)" -Color Gray
    exit 1
}
Write-Log ""

# Get the directory of this PowerShell script (project root)
$ProjectDir = $PSScriptRoot
Set-Location -Path $ProjectDir
Write-Log "Project Directory: $ProjectDir" -Color White

# --- Virtual Environment ---
$VenvDir = Join-Path -Path $ProjectDir -ChildPath "install\.venv"
$VenvActivateScript = Join-Path -Path $VenvDir -ChildPath "Scripts\Activate.ps1"
$PythonwExe = Join-Path -Path $VenvDir -ChildPath "Scripts\pythonw.exe"

if (-not (Test-Path -Path $VenvActivateScript)) {
    Write-Log "Creating Python virtual environment in install\.venv ..." -Color White
    try {
        py -3.12 -m venv $VenvDir
        if ($LASTEXITCODE -ne 0) { throw "Failed to create venv." }
        Write-Log "Virtual environment created successfully." -Color Green
    } catch {
        Write-Log "ERROR: Failed to create virtual environment. Check Python installation." -Color Red
        Write-Log "Error details: $($_.Exception.Message)" -Color Gray
        exit 1
    }
} else {
    Write-Log "Using existing virtual environment in install\.venv." -Color White
}
Write-Log ""

# --- Activate Venv and Install Requirements ---
Write-Log "Activating environment and installing dependencies from requirements.txt..." -Color White
try {
    # Activate by executing the activation script (dot-sourcing)
    . $VenvActivateScript
    if ($LASTEXITCODE -ne 0) { throw "Failed to activate venv." }

    Write-Log "Installing packages (this may take a moment)..." -Color White
    pip install -r requirements.txt --no-warn-script-location
    if ($LASTEXITCODE -ne 0) { throw "Failed to install requirements." }

    Write-Log "Dependencies installed successfully." -Color Green
} catch {
    Write-Log "ERROR: Failed during environment activation or dependency installation." -Color Red
    Write-Log "Check install\.venv folder, requirements.txt, and network connection." -Color Yellow
    Write-Log "Error details: $($_.Exception.Message)" -Color Gray
    exit 1
}
Write-Log ""

# --- Launch the Wizard ---
$WizardScript = Join-Path -Path $ProjectDir -ChildPath "install\main.py"
Write-Log "Launching Arcade Station Setup Wizard..." -Color Cyan
try {
    # Using Start-Process with -WindowStyle Hidden to hide the console
    Write-Log "Starting without console window using pythonw.exe" -NoConsole
    
    # Use pythonw.exe instead of python.exe to avoid console window
    if (Test-Path -Path $PythonwExe) {
        # Launch without console window
        Start-Process -FilePath $PythonwExe -ArgumentList $WizardScript -NoNewWindow
        Write-Log "Wizard launched successfully. UI should appear momentarily." -Color Green
        Write-Log "Setup will continue in the background; you can close this console." -Color Yellow
    } else {
        # Fallback to regular python if pythonw is not available
        Write-Log "WARNING: pythonw.exe not found, using regular python instead." -Color Yellow
        python $WizardScript
        if ($LASTEXITCODE -ne 0) { 
            Write-Log "Wizard exited with code: $LASTEXITCODE" -Color Yellow
        }
    }
} catch {
    Write-Log "ERROR: Failed to launch the setup wizard." -Color Red
    Write-Log "Error details: $($_.Exception.Message)" -Color Gray
    exit 1
}

Write-Log ""
Write-Log "Setup initialized - you can close this window if the installer UI has appeared." -Color Green

# Deactivation is automatic when script exits