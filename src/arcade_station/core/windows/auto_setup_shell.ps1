# Self-elevating script to setup Arcade Station shell
$ErrorActionPreference = "Stop"

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    # Create a new process with admin rights
    $arguments = "& {& '$PSCommandPath'}"
    Start-Process powershell.exe -Verb RunAs -ArgumentList $arguments
    exit
}

# Now running as admin, proceed with setup
$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$setupScript = Join-Path -Path $scriptDir -ChildPath "setup_windows_shell.ps1"

# Run the setup script
& $setupScript 