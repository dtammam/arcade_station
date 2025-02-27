<#
.SYNOPSIS
    Launch MAME.exe in an unobtrusive way.
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

# Add this function to set window focus
function Set-WindowFocus {
    param (
        [int]$ProcessId
    )
    
    Add-Type @"
        using System;
        using System.Runtime.InteropServices;
        
        public class WindowFocus {
            [DllImport("user32.dll")]
            [return: MarshalAs(UnmanagedType.Bool)]
            public static extern bool SetForegroundWindow(IntPtr hWnd);
            
            [DllImport("user32.dll")]
            public static extern IntPtr GetForegroundWindow();
            
            [DllImport("user32.dll")]
            [return: MarshalAs(UnmanagedType.Bool)]
            public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
            
            [DllImport("user32.dll")]
            public static extern bool AllowSetForegroundWindow(int processId);
            
            [DllImport("user32.dll")]
            public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, int dwExtraInfo);
        }
"@

    try {
        $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        if ($process) {
            # Force allowing foreground window changes
            [void][WindowFocus]::AllowSetForegroundWindow($ProcessId)
            
            # Try to set focus multiple times
            for ($i = 0; $i -lt 3; $i++) {
                # Show and maximize the window
                [void][WindowFocus]::ShowWindow($process.MainWindowHandle, 3) # 3 = Maximize
                [void][WindowFocus]::SetForegroundWindow($process.MainWindowHandle)
                
                # Simulate Alt key press to force focus refresh
                [WindowFocus]::keybd_event(0x12, 0, 0, 0) # Alt press
                Start-Sleep -Milliseconds 100
                [WindowFocus]::keybd_event(0x12, 0, 2, 0) # Alt release (2 = KEYEVENTF_KEYUP)
                
                Start-Sleep -Milliseconds 500
            }
            Write-Information "Set window focus for process $ProcessId"
            return $true
        }
        return $false
    }
    catch {
        Write-Information "Failed to set window focus: $_"
        return $false
    }
}

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
        $process = Start-Process -FilePath "$ExecutablePath\$Executable" -ArgumentList "$IniPath $ROM -state $State" -PassThru
        return $process
    }

    # Start MAME.exe
    Write-Information "Launching MAME.exe with ROM: [$ROM], State: [$State]..."
    $mameProcess = Start-MAME -ROM $ROM -State $State -ExecutablePath $ExecutablePath -Executable $Executable -IniPath $IniPath
    Write-Information "Launched MAME.exe with PID: $($mameProcess.Id)"
    
    # Give MAME time to initialize
    Start-Sleep -Seconds 2
    
    # Set focus on the MAME window to fix black screen issue
    Set-WindowFocus -ProcessId $mameProcess.Id
    
    $Script:exitCode = 0
} catch {
    Start-Sleep -Seconds 10
    Write-Information "Script failed with the following exception: [$($_.Message)]"
    $Script:exitCode = 1
} finally {
    exit $script:exitCode
}