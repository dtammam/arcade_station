#Requires -Version 5.1

# Set strict mode and error action
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "== Arcade Station Setup =="
Write-Host ""
Write-Host "Verifying Python 3.12 installation..."

# Check for Python 3.12 using Get-Command (more reliable than just running py)
$Python312Info = Get-Command py -ErrorAction SilentlyContinue
if (-not $Python312Info) {
    Write-Host "ERROR: The 'py' command (Python Launcher) was not found." -ForegroundColor Red
    Write-Host "Please install Python 3.12 (recommend 3.12.9) from python.org" -ForegroundColor Yellow
    Write-Host "Ensure it was added to your system PATH during installation." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Try running the version check
try {
    py -3.12 -V *> $null # Redirect stdout and stderr to null
    if ($LASTEXITCODE -ne 0) { throw "py -3.12 command failed." }
    Write-Host "Found compatible Python 3.12." -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python 3.12 was not found or failed using the 'py -3.12' command." -ForegroundColor Red
    Write-Host "Ensure Python 3.12 (recommend 3.12.9) is installed and accessible via 'py -3.12'." -ForegroundColor Yellow
    Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Gray
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Get the directory of this PowerShell script (project root)
$ProjectDir = $PSScriptRoot
Set-Location -Path $ProjectDir
Write-Host "Project Directory: $ProjectDir"

# --- Virtual Environment ---
$VenvDir = Join-Path -Path $ProjectDir -ChildPath ".venv"
$VenvActivateScript = Join-Path -Path $VenvDir -ChildPath "Scripts\Activate.ps1"

if (-not (Test-Path -Path $VenvActivateScript)) {
    Write-Host "Creating Python virtual environment in .\venv ..."
    try {
        py -3.12 -m venv $VenvDir
        if ($LASTEXITCODE -ne 0) { throw "Failed to create venv." }
        Write-Host "Virtual environment created successfully." -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Failed to create virtual environment. Check Python installation." -ForegroundColor Red
        Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Gray
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "Using existing virtual environment in .\venv."
}
Write-Host ""

# --- Activate Venv and Install Requirements ---
Write-Host "Activating environment and installing dependencies from requirements.txt..."
try {
    # Activate by executing the activation script (dot-sourcing)
    . $VenvActivateScript
    if ($LASTEXITCODE -ne 0) { throw "Failed to activate venv." }

    Write-Host "Installing packages (this may take a moment)..."
    pip install -r requirements.txt --no-warn-script-location
    if ($LASTEXITCODE -ne 0) { throw "Failed to install requirements." }

    Write-Host "Dependencies installed successfully." -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed during environment activation or dependency installation." -ForegroundColor Red
    Write-Host "Check .\venv folder, requirements.txt, and network connection." -ForegroundColor Yellow
    Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Gray
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# --- Launch the Wizard ---
$WizardScript = Join-Path -Path $ProjectDir -ChildPath "install\main.py"
Write-Host "Launching Arcade Station Setup Wizard..."
try {
    # Run the python script using the interpreter from the activated venv
    python $WizardScript
    if ($LASTEXITCODE -ne 0) { Write-Host "Wizard exited with code: $LASTEXITCODE" -ForegroundColor Yellow }
} catch {
    Write-Host "ERROR: Failed to launch the setup wizard." -ForegroundColor Red
    Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Gray
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Setup wizard finished."

# Deactivation is automatic when script exits