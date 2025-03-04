#Requires -RunAsAdministrator

# Script to configure the Windows shell to use Arcade Station as a replacement
# Must be run as Administrator

$ErrorActionPreference = "Stop"

# Get the current directory where the script is located
$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
# Navigate to project root
$projectRoot = (Get-Item $scriptDir).parent.parent.parent.parent.FullName
$batchFilePath = Join-Path -Path $scriptDir -ChildPath "arcade_station_start.bat"

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

# Check if the key exists
if (-not (Test-Path -Path $shellKey)) {
    Write-Error "Windows shell registry key not found."
    exit 1
}

# Backup the current shell value
try {
    $currentShell = Get-ItemProperty -Path $shellKey -Name "Shell" | Select-Object -ExpandProperty "Shell"
    Write-Host "Current shell is: $currentShell"
    
    # Create backup in registry
    Set-ItemProperty -Path $shellKey -Name "OriginalShell" -Value $currentShell -Type String
    Write-Host "Backed up original shell to registry key 'OriginalShell'"
    
    # Also save to a file
    $backupPath = Join-Path -Path $projectRoot -ChildPath "shell_backup.txt"
    $currentShell | Out-File -FilePath $backupPath
    Write-Host "Backed up original shell to file: $backupPath"
}
catch {
    Write-Warning "Failed to backup current shell: $_"
    # Continue anyway
}

# Set new shell value
try {
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
Write-Host "It is recommended to test this in a virtual machine or secondary user account first."
Read-Host -Prompt "Press Enter to restart..." 
Restart-ComputerSafely