<#
.SYNOPSIS
    Restart the computer.
.NOTES
    This script is used to restart the computer.
#>

# Parameters to launch the .ps1 script from a command line
param (
)

# Import core modules relevant for all scripts
[string]$coreFunctionsModule = Join-Path -Path $PSScriptRoot -ChildPath "core_functions.psm1"
Import-Module -Name $coreFunctionsModule -Force

# Restart the computer
Restart-ComputerSafely