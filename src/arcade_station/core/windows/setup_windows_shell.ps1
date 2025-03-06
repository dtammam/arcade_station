#Requires -RunAsAdministrator

# Script to configure the Windows shell to use Arcade Station as a replacement
# Must be run as Administrator

$ErrorActionPreference = "Stop"

# Get the current directory where the script is located
$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$batchFilePath = Join-Path -Path $scriptDir -ChildPath "arcade_station_start.bat"

# Import core functions module
$coreFunctionsModule = Join-Path -Path $scriptDir -ChildPath "core_functions.psm1"
Import-Module -Name $coreFunctionsModule -Force

# Ensure the batch file exists
if (-not (Test-Path -Path $batchFilePath)) {
    Write-Error "The arcade_station_start.bat file was not found in the directory: $scriptDir"
    exit 1
}

# Convert to absolute path and ensure proper quoting
$batchFileAbsPath = (Resolve-Path -Path $batchFilePath).Path
$shellCommand = "`"$batchFileAbsPath`""

# Registry key for the Windows shell
$shellKey = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"

# Set new shell value
try {
    # Save current shell as backup
    $currentShell = Get-ItemProperty -Path $shellKey -Name "Shell" | Select-Object -ExpandProperty "Shell"
    Set-ItemProperty -Path $shellKey -Name "OriginalShell" -Value $currentShell -Type String
    
    # Set new shell
    Set-ItemProperty -Path $shellKey -Name "Shell" -Value $shellCommand -Type String
    Write-Host "Successfully set Arcade Station as the shell replacement."
    Write-Host "The new shell command is: $shellCommand"
}
catch {
    Write-Error "Failed to set new shell: $_"
    exit 1
}

Write-Host "`nWARNING: The next time you log in, Arcade Station will replace your Windows shell."
Write-Host "To restore your original shell, run restore_windows_shell.ps1 as Administrator."
Read-Host -Prompt "Press Enter to restart..." 
Restart-ComputerSafely