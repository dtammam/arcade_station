#Requires -RunAsAdministrator

# Script to configure the Windows shell to use Arcade Station as a replacement
# Must be run as Administrator

$ErrorActionPreference = "Stop"

# Get the current directory where the script is located
$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$batchFilePath = Join-Path -Path $scriptDir -ChildPath "launch_arcade_station.bat"

# Import core functions module
$coreFunctionsModule = Join-Path -Path $scriptDir -ChildPath "core_functions.psm1"
Import-Module -Name $coreFunctionsModule -Force

# Ensure the batch file exists
if (-not (Test-Path -Path $batchFilePath)) {
    Write-Error "The launch_arcade_station.bat file was not found in the directory: [$scriptDir]"
    exit 1
}

# Convert to absolute path and ensure proper quoting
$batchFileAbsPath = (Resolve-Path -Path $batchFilePath).Path

# Create scheduled task to run batch file with highest privileges
$taskName = "ArcadeStationShell"
$taskAction = New-ScheduledTaskAction -Execute $batchFileAbsPath
$taskTrigger = New-ScheduledTaskTrigger -AtStartup
$taskPrincipal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$taskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Remove existing task if it exists
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# Create the task
Register-ScheduledTask -TaskName $taskName -Action $taskAction -Trigger $taskTrigger -Principal $taskPrincipal -Settings $taskSettings

# Registry key for the Windows shell
$shellKey = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
$shellValue = "schtasks.exe /run /tn `"$taskName`""

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
    Write-Error "Failed to restore original shell: [$_]"
    exit 1
}

Restart-ComputerSafely