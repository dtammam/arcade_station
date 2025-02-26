#Requires -RunAsAdministrator

# Script to restore the original Windows shell
# Must be run as Administrator

$ErrorActionPreference = "Stop"

# Get the current directory where the script is located
$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
# Navigate to project root
$projectRoot = (Get-Item $scriptDir).parent.parent.parent.parent.FullName
$backupPath = Join-Path -Path $projectRoot -ChildPath "shell_backup.txt"

# Registry key for the Windows shell
$shellKey = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"

# Check if the key exists
if (-not (Test-Path -Path $shellKey)) {
    Write-Error "Windows shell registry key not found."
    exit 1
}

# Try to get the original shell value from registry
$originalShell = $null
try {
    $originalShell = Get-ItemProperty -Path $shellKey -Name "OriginalShell" -ErrorAction SilentlyContinue | 
                     Select-Object -ExpandProperty "OriginalShell"
}
catch {
    Write-Warning "Could not find OriginalShell value in registry."
}

# If not found in registry, try to get from backup file
if (-not $originalShell -and (Test-Path -Path $backupPath)) {
    try {
        $originalShell = Get-Content -Path $backupPath -Raw
        $originalShell = $originalShell.Trim()
        Write-Host "Found original shell in backup file: $originalShell"
    }
    catch {
        Write-Warning "Failed to read from backup file: $_"
    }
}

# If still not found, use the Windows default
if (-not $originalShell) {
    $originalShell = "explorer.exe"
    Write-Warning "No backup found. Using default Windows shell: $originalShell"
}

# Display current shell
try {
    $currentShell = Get-ItemProperty -Path $shellKey -Name "Shell" | Select-Object -ExpandProperty "Shell"
    Write-Host "Current shell is: $currentShell"
}
catch {
    Write-Warning "Failed to get current shell: $_"
}

# Set original shell value
try {
    Set-ItemProperty -Path $shellKey -Name "Shell" -Value $originalShell -Type String
    Write-Host "Successfully restored original shell: $originalShell"
    
    # Clean up the backup registry key if it exists
    if (Get-ItemProperty -Path $shellKey -Name "OriginalShell" -ErrorAction SilentlyContinue) {
        Remove-ItemProperty -Path $shellKey -Name "OriginalShell"
        Write-Host "Removed OriginalShell registry backup."
    }
}
catch {
    Write-Error "Failed to restore original shell: $_"
    exit 1
}

Write-Host "`nYour original Windows shell has been restored."
Write-Host "Changes will take effect at next login."
Read-Host -Prompt "Press Enter to continue..." 