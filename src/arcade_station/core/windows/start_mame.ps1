<#
.SYNOPSIS
    Launches MAME.exe with specific ROM and state for Arcade Station.
.DESCRIPTION
    This script provides a controlled way to launch MAME.exe, particularly for
    573 rhythm games. It handles:
    - Proper working directory setup
    - ROM and save state loading
    - Window focus management
    - Multiple focus attempts with increasing delays
.PARAMETER ROM
    The name of the ROM to load (required).
.PARAMETER State
    The save state to load (optional).
.PARAMETER ExecutablePath
    The path to the MAME executable directory.
.PARAMETER Executable
    The name of the MAME executable file.
.PARAMETER IniPath
    The path to the MAME configuration file.
.NOTES
    This script is specifically designed for Arcade Station's MAME integration.
    It includes sophisticated window focus management to ensure the MAME window
    becomes the foreground window after launch.
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
        [int]$ProcessId,
        [string]$WindowTitle
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
            
            [DllImport("user32.dll")]
            public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
        }
"@

    try {
        # Method 1: Find by process ID
        if ($ProcessId -gt 0) {
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
        }
        
        # Method 2: Try to find window by title substring
        if (-not [string]::IsNullOrEmpty($WindowTitle)) {
            Write-Information "Looking for window with title containing: $WindowTitle"
            $processes = Get-Process | Where-Object {$_.MainWindowTitle -like "*$WindowTitle*" -and $_.MainWindowHandle -ne 0}
            
            if ($processes.Count -gt 0) {
                $process = $processes[0]  # Take the first matching process
                Write-Information "Found window: $($process.MainWindowTitle) (PID: $($process.Id))"
                
                # Show and maximize the window
                [void][WindowFocus]::ShowWindow($process.MainWindowHandle, 3) # 3 = Maximize
                [void][WindowFocus]::SetForegroundWindow($process.MainWindowHandle)
                
                # Simulate Alt key press to force focus refresh
                [WindowFocus]::keybd_event(0x12, 0, 0, 0) # Alt press
                Start-Sleep -Milliseconds 100
                [WindowFocus]::keybd_event(0x12, 0, 2, 0) # Alt release (2 = KEYEVENTF_KEYUP)
                
                Write-Information "Set window focus for window with title '$WindowTitle'"
                return $true
            } else {
                Write-Information "No window found with title containing: $WindowTitle"
            }
        }
        
        # Method 3: Fallback - Try to find any MAME window by well-known titles
        $knownMameTitles = @("MAME", $ROM)
        foreach ($title in $knownMameTitles) {
            $processes = Get-Process | Where-Object {$_.MainWindowTitle -like "*$title*" -and $_.MainWindowHandle -ne 0}
            if ($processes.Count -gt 0) {
                $process = $processes[0]
                Write-Information "Found MAME window with title: $($process.MainWindowTitle)"
                
                # Show and maximize the window
                [void][WindowFocus]::ShowWindow($process.MainWindowHandle, 3) # 3 = Maximize
                [void][WindowFocus]::SetForegroundWindow($process.MainWindowHandle)
                
                # Simulate Alt key press to force focus refresh
                [WindowFocus]::keybd_event(0x12, 0, 0, 0) # Alt press
                Start-Sleep -Milliseconds 100
                [WindowFocus]::keybd_event(0x12, 0, 2, 0) # Alt release (2 = KEYEVENTF_KEYUP)
                
                Write-Information "Set window focus for MAME window"
                return $true
            }
        }
        
        # Method 4: Force foreground permission to any process
        [void][WindowFocus]::AllowSetForegroundWindow(-1)  # -1 = ASFW_ANY
        Write-Information "Allowed any process to take foreground focus"
        
        Write-Information "All focus setting methods exhausted"
        return $false
    }
    catch {
        Write-Information "Failed to set window focus: $_"
        return $false
    }
}

# Main execution block
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
        $process = Start-Process -FilePath "$ExecutablePath\$Executable" -ArgumentList "-inipath $IniPath $ROM -state $State" -PassThru
        return $process
    }

    # Start MAME.exe
    Write-Information "Launching MAME.exe with ROM: [$ROM], State: [$State]..."
    $mameProcess = Start-MAME -ROM $ROM -State $State -ExecutablePath $ExecutablePath -Executable $Executable -IniPath $IniPath
    Write-Information "Launched MAME.exe with PID: $($mameProcess.Id)"
    
    # Give MAME time to initialize
    Write-Information "Waiting for MAME window to appear..."
    Start-Sleep -Seconds 3
    
    # Try multiple focus attempts with increasing delay to ensure MAME window gets focus
    for ($attempt = 1; $attempt -le 5; $attempt++) {
        Write-Information "Focus attempt $attempt..."
        
        # Try to find and focus the MAME window
        $focusResult = Set-WindowFocus -ProcessId $mameProcess.Id -WindowTitle $ROM
        
        # If successful, exit the retry loop
        if ($focusResult) {
            Write-Information "Successfully focused MAME window on attempt $attempt"
            break
        }
        
        # Wait a bit longer with each attempt
        Start-Sleep -Seconds ($attempt * 1)
    }
    
    $Script:exitCode = 0
} catch {
    Write-Information "Script failed with the following exception: [$($_.Message)]"
    $Script:exitCode = 1
} finally {
    exit $script:exitCode
}