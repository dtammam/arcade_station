<#
.SYNOPSIS
    Safely restarts the Windows computer for Arcade Station.
.DESCRIPTION
    This script provides a controlled way to restart the computer, ensuring all
    processes are properly terminated before shutdown. It uses the Restart-ComputerSafely
    function from core_functions.psm1 to handle the restart process.
.NOTES
    This script is part of the Arcade Station Windows management suite and should
    be used instead of direct system restart commands to ensure proper cleanup.
#>

# Parameters to launch the .ps1 script from a command line
[CmdletBinding()]
param ()

# Import core modules relevant for all scripts
[string]$coreFunctionsModule = Join-Path -Path $PSScriptRoot -ChildPath "core_functions.psm1"
Import-Module -Name $coreFunctionsModule -Force

# Restart the computer
Restart-ComputerSafely