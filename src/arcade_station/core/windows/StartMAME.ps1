<#
.SYNOPSIS
    Lunch MAME.exe in an unobtrusive way.
.NOTES
    MAME.exe is required for launching 573 rhythm games and it must be opened, using the ROM and save state as arguments.
#>

# Parameters to launch the .ps1 script from a command line
param (
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$ROM,
    [string]$State,
    [string]$ExecutablePath,
    [string]$Executable,
    [string]$IniPath
)

# Import core modules relevant for all scripts
[string]$coreFunctionsModule = Join-Path -Path $PSScriptRoot -ChildPath "core_functions.psm1"
Import-Module -Name $coreFunctionsModule -Force

try {
    Write-Information "Received ROM: [$ROM], State: [$State]"
    # Change the working directory to the directory with MAME in it, does not parse well without it    
    Set-Location -Path $ExecutablePath
    
    # Create our function for launching MAME with the appropriate ROM and state
    function Start-MAME {
        [CmdletBinding()]
        param(
            [Parameter(Mandatory)]
            [ValidateNotNullOrEmpty()]
            [string]$ROM,
            [string]$State,
            [string]$ExecutablePath,
            [string]$Executable,
            [string]$IniPath
        )

        Write-Information "Starting MAME with arguments: [$IniPath $ROM -state $State]"
        Start-Process -FilePath "$ExecutablePath\$Executable" -ArgumentList "$IniPath $ROM -state $State"
    }

    # Start MAME.exe
    Write-Information "Launching MAME.exe with ROM: [$ROM], State: [$State]..."
    Start-MAME -ROM $ROM -State $State -ExecutablePath $ExecutablePath -Executable $Executable -IniPath $IniPath
    Write-Information "Launched MAME.exe."
    $Script:exitCode = 0
} catch {
    Start-Sleep -Seconds 10
    Write-Information "Script failed with the following exception: [$($_.Message)]"
    $Script:exitCode = 1
} finally {
    exit $script:exitCode
}