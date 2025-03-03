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
            
            [DllImport("user32.dll")]
            [return: MarshalAs(UnmanagedType.Bool)]
            public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
            
            // Special window handles
            public static readonly IntPtr HWND_TOPMOST = new IntPtr(-1);
            public static readonly IntPtr HWND_NOTOPMOST = new IntPtr(-2);
            public static readonly IntPtr HWND_TOP = new IntPtr(0);
            
            // SetWindowPos flags
            public const uint SWP_NOSIZE = 0x0001;
            public const uint SWP_NOMOVE = 0x0002;
            public const uint SWP_NOACTIVATE = 0x0010;
            public const uint SWP_SHOWWINDOW = 0x0040;
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
                    # First set window to top-most to ensure it's above all others
                    [void][WindowFocus]::SetWindowPos(
                        $process.MainWindowHandle, 
                        [WindowFocus]::HWND_TOPMOST, 
                        0, 0, 0, 0, 
                        [WindowFocus]::SWP_NOMOVE -bor [WindowFocus]::SWP_NOSIZE -bor [WindowFocus]::SWP_SHOWWINDOW
                    )
                    
                    # Show and maximize the window
                    [void][WindowFocus]::ShowWindow($process.MainWindowHandle, 3) # 3 = Maximize
                    [void][WindowFocus]::SetForegroundWindow($process.MainWindowHandle)
                    
                    # Simulate Alt key press to force focus refresh
                    [WindowFocus]::keybd_event(0x12, 0, 0, 0) # Alt press
                    Start-Sleep -Milliseconds 100
                    [WindowFocus]::keybd_event(0x12, 0, 2, 0) # Alt release (2 = KEYEVENTF_KEYUP)
                    
                    # Keep it top-most for a moment to ensure it gets focus
                    Start-Sleep -Milliseconds 500
                    
                    # Then set back to normal top (but not always-on-top) so it doesn't interfere with other windows later
                    [void][WindowFocus]::SetWindowPos(
                        $process.MainWindowHandle, 
                        [WindowFocus]::HWND_TOP, 
                        0, 0, 0, 0, 
                        [WindowFocus]::SWP_NOMOVE -bor [WindowFocus]::SWP_NOSIZE -bor [WindowFocus]::SWP_SHOWWINDOW
                    )
                }
                Write-Information "Set window focus and z-order for process $ProcessId"
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
                
                # First set window to top-most to ensure it's above all others
                [void][WindowFocus]::SetWindowPos(
                    $process.MainWindowHandle, 
                    [WindowFocus]::HWND_TOPMOST, 
                    0, 0, 0, 0, 
                    [WindowFocus]::SWP_NOMOVE -bor [WindowFocus]::SWP_NOSIZE -bor [WindowFocus]::SWP_SHOWWINDOW
                )
                
                # Show and maximize the window
                [void][WindowFocus]::ShowWindow($process.MainWindowHandle, 3) # 3 = Maximize
                [void][WindowFocus]::SetForegroundWindow($process.MainWindowHandle)
                
                # Simulate Alt key press to force focus refresh
                [WindowFocus]::keybd_event(0x12, 0, 0, 0) # Alt press
                Start-Sleep -Milliseconds 100
                [WindowFocus]::keybd_event(0x12, 0, 2, 0) # Alt release (2 = KEYEVENTF_KEYUP)
                
                # Keep it top-most for a moment to ensure it gets focus
                Start-Sleep -Milliseconds 500
                
                # Then set back to normal top (but not always-on-top)
                [void][WindowFocus]::SetWindowPos(
                    $process.MainWindowHandle, 
                    [WindowFocus]::HWND_TOP, 
                    0, 0, 0, 0, 
                    [WindowFocus]::SWP_NOMOVE -bor [WindowFocus]::SWP_NOSIZE -bor [WindowFocus]::SWP_SHOWWINDOW
                )
                
                Write-Information "Set window focus and z-order for window with title '$WindowTitle'"
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
                
                # First set window to top-most to ensure it's above all others
                [void][WindowFocus]::SetWindowPos(
                    $process.MainWindowHandle, 
                    [WindowFocus]::HWND_TOPMOST, 
                    0, 0, 0, 0, 
                    [WindowFocus]::SWP_NOMOVE -bor [WindowFocus]::SWP_NOSIZE -bor [WindowFocus]::SWP_SHOWWINDOW
                )
                
                # Show and maximize the window
                [void][WindowFocus]::ShowWindow($process.MainWindowHandle, 3) # 3 = Maximize
                [void][WindowFocus]::SetForegroundWindow($process.MainWindowHandle)
                
                # Simulate Alt key press to force focus refresh
                [WindowFocus]::keybd_event(0x12, 0, 0, 0) # Alt press
                Start-Sleep -Milliseconds 100
                [WindowFocus]::keybd_event(0x12, 0, 2, 0) # Alt release (2 = KEYEVENTF_KEYUP)
                
                # Keep it top-most for a moment to ensure it gets focus
                Start-Sleep -Milliseconds 500
                
                # Then set back to normal top (but not always-on-top)
                [void][WindowFocus]::SetWindowPos(
                    $process.MainWindowHandle, 
                    [WindowFocus]::HWND_TOP, 
                    0, 0, 0, 0, 
                    [WindowFocus]::SWP_NOMOVE -bor [WindowFocus]::SWP_NOSIZE -bor [WindowFocus]::SWP_SHOWWINDOW
                )
                
                Write-Information "Set window focus and z-order for MAME window"
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

# Add function to find and force focus on all windows associated with a process
function Set-AllProcessWindowsToTop {
    param (
        [int]$ProcessId
    )
    
    Add-Type @"
        using System;
        using System.Runtime.InteropServices;
        using System.Collections.Generic;

        public class WindowEnumerationHelper
        {
            [DllImport("user32.dll")]
            [return: MarshalAs(UnmanagedType.Bool)]
            public static extern bool EnumWindows(EnumWindowsProc enumProc, IntPtr lParam);

            [DllImport("user32.dll")]
            [return: MarshalAs(UnmanagedType.Bool)]
            public static extern bool EnumChildWindows(IntPtr hwndParent, EnumWindowsProc enumProc, IntPtr lParam);

            [DllImport("user32.dll")]
            public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);

            [DllImport("user32.dll")]
            [return: MarshalAs(UnmanagedType.Bool)]
            public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);

            [DllImport("user32.dll")]
            [return: MarshalAs(UnmanagedType.Bool)]
            public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

            [DllImport("user32.dll")]
            [return: MarshalAs(UnmanagedType.Bool)]
            public static extern bool IsWindowVisible(IntPtr hWnd);

            [DllImport("user32.dll")]
            public static extern bool SetForegroundWindow(IntPtr hWnd);

            public static readonly IntPtr HWND_TOPMOST = new IntPtr(-1);
            public static readonly IntPtr HWND_TOP = new IntPtr(0);
            public const uint SWP_NOSIZE = 0x0001;
            public const uint SWP_NOMOVE = 0x0002;
            public const uint SWP_SHOWWINDOW = 0x0040;

            // Define the delegate for the EnumWindows callback
            public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

            public static List<IntPtr> GetProcessWindows(int processId)
            {
                List<IntPtr> windowHandles = new List<IntPtr>();
                EnumWindows(new EnumWindowsProc((hWnd, lParam) => 
                {
                    uint windowProcessId;
                    GetWindowThreadProcessId(hWnd, out windowProcessId);
                    
                    if (windowProcessId == processId && IsWindowVisible(hWnd))
                    {
                        windowHandles.Add(hWnd);
                        
                        // Also enumerate child windows
                        EnumChildWindows(hWnd, new EnumWindowsProc((childHwnd, childLParam) => 
                        {
                            if (IsWindowVisible(childHwnd))
                            {
                                windowHandles.Add(childHwnd);
                            }
                            return true;
                        }), IntPtr.Zero);
                    }
                    
                    return true;
                }), IntPtr.Zero);
                
                return windowHandles;
            }
        }
"@

    try {
        # Try to get all windows associated with this process
        $windowHandles = [WindowEnumerationHelper]::GetProcessWindows($ProcessId)
        Write-Information "Found $($windowHandles.Count) windows for process ID $ProcessId"

        foreach ($hwnd in $windowHandles) {
            # First set window to top-most to ensure it's above all others
            [void][WindowEnumerationHelper]::SetWindowPos(
                $hwnd, 
                [WindowEnumerationHelper]::HWND_TOPMOST, 
                0, 0, 0, 0, 
                [WindowEnumerationHelper]::SWP_NOMOVE -bor [WindowEnumerationHelper]::SWP_NOSIZE -bor [WindowEnumerationHelper]::SWP_SHOWWINDOW
            )
            
            # Show the window (3 = maximize)
            [void][WindowEnumerationHelper]::ShowWindow($hwnd, 3)
            [void][WindowEnumerationHelper]::SetForegroundWindow($hwnd)
            
            Write-Information "Set window $hwnd to topmost"
        }
        
        if ($windowHandles.Count -gt 0) {
            # After a moment, set windows back to normal top (not always-on-top)
            Start-Sleep -Milliseconds 1000
            
            foreach ($hwnd in $windowHandles) {
                [void][WindowEnumerationHelper]::SetWindowPos(
                    $hwnd, 
                    [WindowEnumerationHelper]::HWND_TOP, 
                    0, 0, 0, 0, 
                    [WindowEnumerationHelper]::SWP_NOMOVE -bor [WindowEnumerationHelper]::SWP_NOSIZE -bor [WindowEnumerationHelper]::SWP_SHOWWINDOW
                )
            }
            return $true
        }
        return $false
    }
    catch {
        Write-Information "Error in Set-AllProcessWindowsToTop: $_"
        return $false
    }
}

# Add function to disable screen saver and power management during game
function Disable-PowerManagement {
    try {
        # Prevent display from turning off
        $null = powercfg -change -monitor-timeout-ac 0
        $null = powercfg -change -monitor-timeout-dc 0
        
        # Prevent system from sleeping
        $null = powercfg -change -standby-timeout-ac 0
        $null = powercfg -change -standby-timeout-dc 0
        
        Write-Information "Disabled power management features"
        return $true
    }
    catch {
        Write-Information "Failed to disable power management: $_"
        return $false
    }
}

# Restore power settings when done
function Restore-PowerManagement {
    try {
        # Restore default display timeout (15 minutes on AC, 5 minutes on battery)
        $null = powercfg -change -monitor-timeout-ac 15
        $null = powercfg -change -monitor-timeout-dc 5
        
        # Restore default sleep timeout (30 minutes on AC, 15 minutes on battery)
        $null = powercfg -change -standby-timeout-ac 30
        $null = powercfg -change -standby-timeout-dc 15
        
        Write-Information "Restored power management features"
        return $true
    }
    catch {
        Write-Information "Failed to restore power management: $_"
        return $false
    }
}

# Main execution block
try {
    Write-Information "Received ROM: [$ROM], State: [$State]"
    # Change the working directory to the directory with MAME in it, does not parse well without it    
    Set-Location -Path $ExecutablePath
    
    # Disable power management to prevent screen blanking
    Disable-PowerManagement
    
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
    Write-Information "Waiting for MAME window to appear..."
    Start-Sleep -Seconds 7
    
    # Try multiple focus attempts with increasing delay to ensure MAME window gets focus
    for ($attempt = 1; $attempt -le 5; $attempt++) {
        Write-Information "Focus attempt $attempt..."
        
        # Try to find and focus the MAME window using the regular method
        $focusResult = Set-WindowFocus -ProcessId $mameProcess.Id -WindowTitle $ROM
        
        # Also try the more comprehensive method to find all windows
        $allWindowsResult = Set-AllProcessWindowsToTop -ProcessId $mameProcess.Id
        
        # If either succeeded, exit the retry loop
        if ($focusResult -or $allWindowsResult) {
            Write-Information "Successfully focused MAME window on attempt $attempt"
            break
        }
        
        # Wait a bit longer with each attempt
        Start-Sleep -Seconds ($attempt * 1)
    }
    
    # Final focus attempt using both methods in sequence after all other processing
    Write-Information "Performing final focus attempt..."
    Set-WindowFocus -ProcessId $mameProcess.Id -WindowTitle $ROM
    Set-AllProcessWindowsToTop -ProcessId $mameProcess.Id
    
    $Script:exitCode = 0
} catch {
    Write-Information "Script failed with the following exception: [$($_.Message)]"
    $Script:exitCode = 1
} finally {
    # After 30 seconds, restore power management settings
    Start-Sleep -Seconds 30
    Restore-PowerManagement
    exit $script:exitCode
}