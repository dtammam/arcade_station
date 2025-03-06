#Requires -RunAsAdministrator

# Script to restore the original Windows shell
# Must be run as Administrator

$ErrorActionPreference = "Stop"

# Get the current directory where the script is located
$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

# Import core functions module
$coreFunctionsModule = Join-Path -Path $scriptDir -ChildPath "core_functions.psm1"
Import-Module -Name $coreFunctionsModule -Force

# Registry key for the Windows shell
$shellKey = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"

# Try to get the original shell value from registry
try {
    $originalShell = Get-ItemProperty -Path $shellKey -Name "OriginalShell" -ErrorAction SilentlyContinue | 
                     Select-Object -ExpandProperty "OriginalShell"
    
    # If found, use it
    if ($originalShell) {
        Write-Host "Found original shell in registry: $originalShell"
    } else {
        # Default to explorer.exe if no backup found
        $originalShell = "explorer.exe"
        Write-Host "No backup found. Using default Windows shell: $originalShell"
    }
    
    # Set original shell value
    Set-ItemProperty -Path $shellKey -Name "Shell" -Value $originalShell -Type String
    Write-Host "Successfully restored shell to: $originalShell"
    
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
Read-Host -Prompt "Press Enter to restart..." 
Restart-ComputerSafely