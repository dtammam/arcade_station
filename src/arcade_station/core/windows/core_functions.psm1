function Update-RegistryKey {
    <#
    .SYNOPSIS
        Updates a registry key with a specified value.
    .PARAMETER Path
        The registry path.
    .PARAMETER Name
        The name of the registry key.
    .PARAMETER Value
        The value to set.
    #>
    param (
        [string]$Path,
        [string]$Name,
        [string]$Value
    )

    try {
        New-ItemProperty -Path $Path -Name $Name -Value $Value -PropertyType String -Force
        Write-Information "Modified [$Name] to [$Value] at [$Path]."
    } catch {
        Write-Information "Failed to update registry key: [$($_.Exception.Message)]"
    }
}

function Start-ProcessSilently {
    <#
    .SYNOPSIS
        Starts a process silently with minimal UI flashing.
    .PARAMETER FilePath
        The path to the executable or file to start.
    .PARAMETER WorkingDirectory
        The working directory for the process.
    .PARAMETER Arguments
        Optional arguments to pass to the process.
    .PARAMETER WindowStyle
        The window style (Hidden, Normal, Minimized, Maximized). Defaults to Hidden.
    .EXAMPLE
        Start-ProcessSilently -FilePath "C:\path\to\game.exe" -WorkingDirectory "C:\path\to" -WindowStyle Hidden
    #>
    param (
        [Parameter(Mandatory=$true)]
        [string]$FilePath,
        
        [Parameter(Mandatory=$false)]
        [string]$WorkingDirectory = "",
        
        [Parameter(Mandatory=$false)]
        [string]$Arguments = "",
        
        [Parameter(Mandatory=$false)]
        [ValidateSet("Hidden", "Normal", "Minimized", "Maximized")]
        [string]$WindowStyle = "Hidden"
    )

    try {
        # Convert window style to integer value
        $windowStyleValue = switch ($WindowStyle) {
            "Hidden" { 0 }
            "Normal" { 1 }
            "Minimized" { 2 }
            "Maximized" { 3 }
            default { 0 }
        }

        # Use ProcessStartInfo for more control
        $startInfo = New-Object System.Diagnostics.ProcessStartInfo
        $startInfo.FileName = $FilePath
        
        if ($Arguments) {
            $startInfo.Arguments = $Arguments
        }
        
        if ($WorkingDirectory) {
            $startInfo.WorkingDirectory = $WorkingDirectory
        }
        
        $startInfo.WindowStyle = $windowStyleValue
        $startInfo.CreateNoWindow = ($WindowStyle -eq "Hidden")
        
        # Start the process
        $process = [System.Diagnostics.Process]::Start($startInfo)
        
        Write-Information "Started process [$FilePath] with PID [$($process.Id)]"
        return $process
    }
    catch {
        Write-Information "Failed to start process [$FilePath]: [$($_.Exception.Message)]"
        return $null
    }
}

function Restart-ComputerSafely {
    <#
    .SYNOPSIS
        Restarts the computer safely.
    #>
    try {
        Write-Information "Restarting computer now..."
        Restart-Computer -Force
    } catch {
        Write-Information "Failed to restart computer: [$($_.Exception.Message)]"
    }
}