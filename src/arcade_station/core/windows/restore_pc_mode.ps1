<#
.SYNOPSIS
    Restores Windows to normal PC mode from Arcade Station kiosk mode.
.DESCRIPTION
    This script reverts Windows configuration changes made by setup_kiosk_mode.ps1,
    restoring the system to standard PC operation. It:
    - Sets the default Windows shell back to explorer.exe
    - Restores default window focus behavior
    - Requires administrative privileges to modify system settings
.PARAMETER None
    This script takes no parameters.
.NOTES
    This script must be run as Administrator to modify system settings.
    It will automatically restart the computer after making changes.
#>

#Requires -RunAsAdministrator

# Script to restore Windows to normal PC mode
# Must be run as Administrator

$ErrorActionPreference = "Stop"

# Get the current directory where the script is located
$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

# Import core functions module
$coreFunctionsModule = Join-Path -Path $scriptDir -ChildPath "core_functions.psm1"
Import-Module -Name $coreFunctionsModule -Force

# Registry key for the Windows shell
$shellKey = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
$shellValue = "explorer.exe"

# Window flicker management
$foregroundLockTimeout = 200000
$foregroundFlashCount = 7

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
    Write-Error "Failed to restore PC mode: [$_]"
    exit 1
}

Restart-ComputerSafely