<#
.SYNOPSIS
    Configures Windows to run Arcade Station in kiosk mode.
.DESCRIPTION
    This script sets up Windows to automatically launch Arcade Station on startup,
    effectively creating a kiosk-like environment. It:
    - Sets Arcade Station as the Windows shell
    - Configures window focus behavior to minimize flicker
    - Requires administrative privileges to modify system settings
.PARAMETER None
    This script takes no parameters.
.NOTES
    This script must be run as Administrator to modify system settings.
    It will automatically restart the computer after making changes.
    The script expects launch_arcade_station.bat to be in the project root directory.
#>

#Requires -RunAsAdministrator

# Script to configure Windows to use Arcade Station in kiosk mode
# Must be run as Administrator

$ErrorActionPreference = "Stop"

# Get the current directory where the script is located
$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
# Navigate up from core/windows to the root directory
$rootDir = (Resolve-Path -Path (Join-Path -Path $scriptDir -ChildPath "..\..\..\..")).Path
$launchExePath = Join-Path -Path $rootDir -ChildPath "launch_arcade_station.bat"

# Import core functions module
$coreFunctionsModule = Join-Path -Path $scriptDir -ChildPath "core_functions.psm1"
Import-Module -Name $coreFunctionsModule -Force

# Ensure the launch executable exists
if (-not (Test-Path -Path $launchExePath)) {
    Write-Error "The launch_arcade_station.bat file was not found in the root directory: [$rootDir]"
    exit 1
}

# Registry key for the Windows shell
$shellKey = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
$shellValue = "`"$launchExePath`""

# Window flicker management
$foregroundLockTimeout = 3000
$foregroundFlashCount = 5

try {
    # Set shell value
    Set-ItemProperty -Path $shellKey -Name "Shell" -Value $shellValue -Type String
    Write-Host "Set Shell to [$shellValue]"

    # Set registry values for default foreground window behavior
    Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "ForegroundLockTimeout" -Value $foregroundLockTimeout -Type DWord
    Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "ForegroundFlashCount" -Value $foregroundFlashCount -Type DWord
    Write-Host "Set ForegroundLockTimeout to [$foregroundLockTimeout] and ForegroundFlashCount to [$foregroundFlashCount]"
}
catch {
    Write-Error "Failed to set up kiosk mode: [$_]"
    exit 1
}

Restart-ComputerSafely