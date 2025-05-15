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