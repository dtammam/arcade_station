<#
.SYNOPSIS
    Bring a computer out of PC mode into Kiosk mode.
.NOTES
    Replace shell to be a script that launches all utilities, as opposed to explorer.exe.
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
	$value = '"C:\pegasus\StartFrontendApps.exe"' # Update with installer later
    
    Write-Information "Setting [$($name)] to [$($value)]..."
    New-ItemProperty -Path $registryPath -Name $name -Value $value -PropertyType String -Force
    Write-Information "Modified [$($name)] to [$($value)]."

    Write-Information "Restarting computer now..."
    Restart-ComputerSafely
    $script:exitCode = 0
} catch {
    Write-Information "Script failed with the following exception: [$($_.Message)]"
    $script:exitCode = 1
} finally {
    exit $script:exitCode
}