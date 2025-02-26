#Requires -RunAsAdministrator

# This is a wrapper script that calls the platform-specific Windows shell restore script

# Get the current directory where the script is located
$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$restoreScript = Join-Path -Path $scriptDir -ChildPath "src\arcade_station\core\windows\restore_windows_shell.ps1"

# Ensure the script exists
if (-not (Test-Path -Path $restoreScript)) {
    Write-Error "The restore_windows_shell.ps1 script was not found at: $restoreScript"
    exit 1
}

# Run the platform-specific script
& $restoreScript 