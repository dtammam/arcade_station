<#
.SYNOPSIS
    Bring a computer out of kiosk mode back to PC mode
.NOTES
    Replace shell to be explorer.exe as a standard PC shell.
.LINK
    Shell Explorer is cool, but isn't supported on all editions of Windows - https://learn.microsoft.com/en-us/windows/configuration/assigned-access/shell-launcher
#>

# Import core modules relevant for all scripts
[string]$coreFunctionsModule = Join-Path -Path $PSScriptRoot -ChildPath "core_functions.psm1"
Import-Module -Name $coreFunctionsModule -Force

try {
    Write-Information "Creating variables."
    $registryPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
    $name = 'Shell'
    $value = 'explorer.exe'
    
    Write-Information "Setting [$($name)] to [$($value)]..."
    New-ItemProperty -Path $registryPath -Name $name -Value $value -PropertyType String -Force
    Write-Information "Modified [$($name)] to [$($value)]."

    Write-Information "Restarting computer now..."
    Restart-ComputerSafely
    $Script:exitCode = 0
} catch {
    Write-Information "Script failed with the following exception: [$($_.Message)]"
    $Script:exitCode = 1
} finally {
    exit $Script:exitCode
}