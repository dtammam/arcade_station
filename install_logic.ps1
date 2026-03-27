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

# Write-InstallLog: named to avoid collision with any built-in Write-Log cmdlet.
function Write-InstallLog {
    # Write-Host is intentional: interactive installer uses colored console output for user visibility.
    [Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSAvoidUsingWriteHost', '',
        Justification = 'Intentional colored console output in interactive installer script')]
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

Write-InstallLog "== Arcade Station Setup ==" -Color Cyan
Write-InstallLog "Log file: $LogFile" -Color Gray
Write-InstallLog ""
Write-InstallLog "Verifying Python 3.12 installation..." -Color White

# Check for Python 3.12 using Get-Command (more reliable than just running py)
$Python312Info = Get-Command py -ErrorAction SilentlyContinue
if (-not $Python312Info) {
    Write-InstallLog "ERROR: The 'py' command (Python Launcher) was not found." -Color Red
    Write-InstallLog "Please install Python 3.12 (recommend 3.12.9) from python.org" -Color Yellow
    Write-InstallLog "Ensure it was added to your system PATH during installation." -Color Yellow
    exit 1
}

# Try running the version check
try {
    py -3.12 -V *> $null # Redirect stdout and stderr to null
    if ($LASTEXITCODE -ne 0) { throw "py -3.12 command failed." }
    Write-InstallLog "Found compatible Python 3.12." -Color Green
} catch {
    Write-InstallLog "ERROR: Python 3.12 was not found or failed using the 'py -3.12' command." -Color Red
    Write-InstallLog "Ensure Python 3.12 (recommend 3.12.9) is installed and accessible via 'py -3.12'." -Color Yellow
    Write-InstallLog "Error details: $($_.Exception.Message)" -Color Gray
    exit 1
}
Write-InstallLog ""

# Get the directory of this PowerShell script (project root)
$ProjectDir = $PSScriptRoot
Set-Location -Path $ProjectDir
Write-InstallLog "Project Directory: $ProjectDir" -Color White

# --- Virtual Environment ---
$VenvDir = Join-Path -Path $ProjectDir -ChildPath "install\.venv"
$VenvActivateScript = Join-Path -Path $VenvDir -ChildPath "Scripts\Activate.ps1"
$PythonwExe = Join-Path -Path $VenvDir -ChildPath "Scripts\pythonw.exe"

if (-not (Test-Path -Path $VenvActivateScript)) {
    Write-InstallLog "Creating Python virtual environment in install\.venv ..." -Color White
    try {
        py -3.12 -m venv $VenvDir
        if ($LASTEXITCODE -ne 0) { throw "Failed to create venv." }
        Write-InstallLog "Virtual environment created successfully." -Color Green
    } catch {
        Write-InstallLog "ERROR: Failed to create virtual environment. Check Python installation." -Color Red
        Write-InstallLog "Error details: $($_.Exception.Message)" -Color Gray
        exit 1
    }
} else {
    Write-InstallLog "Using existing virtual environment in install\.venv." -Color White
}
Write-InstallLog ""

# --- Activate Venv and Install Requirements ---
Write-InstallLog "Activating environment and installing dependencies from requirements.txt..." -Color White
try {
    # Activate by executing the activation script (dot-sourcing)
    . $VenvActivateScript
    if ($LASTEXITCODE -ne 0) { throw "Failed to activate venv." }

    Write-InstallLog "Installing packages (this may take a moment)..." -Color White
    pip install -r requirements.txt --no-warn-script-location
    if ($LASTEXITCODE -ne 0) { throw "Failed to install requirements." }

    Write-InstallLog "Dependencies installed successfully." -Color Green
} catch {
    Write-InstallLog "ERROR: Failed during environment activation or dependency installation." -Color Red
    Write-InstallLog "Check install\.venv folder, requirements.txt, and network connection." -Color Yellow
    Write-InstallLog "Error details: $($_.Exception.Message)" -Color Gray
    exit 1
}
Write-InstallLog ""

# --- Launch the Wizard ---
$WizardScript = Join-Path -Path $ProjectDir -ChildPath "install\main.py"
Write-InstallLog "Launching Arcade Station Setup Wizard..." -Color Cyan
try {
    # Using Start-Process with -WindowStyle Hidden to hide the console
    Write-InstallLog "Starting without console window using pythonw.exe" -NoConsole

    # Use pythonw.exe instead of python.exe to avoid console window
    if (Test-Path -Path $PythonwExe) {
        # Launch without console window
        Start-Process -FilePath $PythonwExe -ArgumentList $WizardScript -NoNewWindow
        Write-InstallLog "Wizard launched successfully. UI should appear momentarily." -Color Green
        Write-InstallLog "Setup will continue in the background; you can close this console." -Color Yellow
    } else {
        # Fallback to regular python if pythonw is not available
        Write-InstallLog "WARNING: pythonw.exe not found, using regular python instead." -Color Yellow
        python $WizardScript
        if ($LASTEXITCODE -ne 0) {
            Write-InstallLog "Wizard exited with code: $LASTEXITCODE" -Color Yellow
        }
    }
} catch {
    Write-InstallLog "ERROR: Failed to launch the setup wizard." -Color Red
    Write-InstallLog "Error details: $($_.Exception.Message)" -Color Gray
    exit 1
}

Write-InstallLog ""
Write-InstallLog "Setup initialized - you can close this window if the installer UI has appeared." -Color Green

# Deactivation is automatic when script exits
