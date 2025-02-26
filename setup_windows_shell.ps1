#Requires -RunAsAdministrator

# This is a wrapper script that calls the platform-specific Windows shell setup script

# Get the current directory where the script is located
$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$setupScript = Join-Path -Path $scriptDir -ChildPath "src\arcade_station\core\windows\setup_windows_shell.ps1"

# Ensure the script exists
if (-not (Test-Path -Path $setupScript)) {
    Write-Error "The setup_windows_shell.ps1 script was not found at: $setupScript"
    exit 1
}

# Run the platform-specific script
& $setupScript 