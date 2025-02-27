<#
.SYNOPSIS
    Manages iCloud Photo uploads consistently from a Windows machine.
.DESCRIPTION
    This script restarts iCloud services regularly and cleans up the upload directory to ensure photos are processed.
    The script uses parameters from the screenshot_config.toml file.
.NOTES
    Created for Arcade Station to manage iCloud photo uploads.
#>

param (
    [Parameter(Mandatory=$true)]
    [string]$AppleServicesPath,
    
    [Parameter(Mandatory=$true)]
    [string[]]$ProcessesToRestart,
    
    [Parameter(Mandatory=$true)]
    [string]$UploadDirectory,
    
    [Parameter(Mandatory=$true)]
    [int]$IntervalSeconds,
    
    [Parameter(Mandatory=$true)]
    [bool]$DeleteAfterUpload
)

# Import common logging functions
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$parentDir = Split-Path -Parent $scriptDir
$commonDir = Join-Path $parentDir "common"
$coreFunctionsPath = Join-Path $commonDir "core_functions.ps1"

if (Test-Path $coreFunctionsPath) {
    . $coreFunctionsPath
} else {
    function Write-Log {
        param([string]$Message)
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Write-Host "[$timestamp] $Message"
    }
}

# Variable declaration
[int]$deletedCount = 0

try {
    Write-Log "Starting iCloud upload management service"
    
    # Log and validate parameters
    Write-Log "Parameters received:"
    Write-Log "  AppleServicesPath: $AppleServicesPath"
    Write-Log "  ProcessesToRestart: $($ProcessesToRestart -join ', ')"
    Write-Log "  UploadDirectory: $UploadDirectory"
    Write-Log "  IntervalSeconds: $IntervalSeconds"
    Write-Log "  DeleteAfterUpload: $DeleteAfterUpload"
    
    # Ensure IntervalSeconds is valid
    if ($IntervalSeconds -lt 10) {
        Write-Log "Warning: IntervalSeconds is too low ($IntervalSeconds). Setting to default of 300 seconds."
        $IntervalSeconds = 300
    }
    
    # Main loop
    while ($true) {
        Write-Log "Processing cycle started"
        
        # Stop each process in the processes to restart array
        foreach ($process in $ProcessesToRestart) {
            Write-Log "Stopping [$process]..."
            if (-not (Get-Process $process -ErrorAction SilentlyContinue)) {
                Write-Log "[$process] not running. Continuing..."
            } else {
                Stop-Process -Name $process -Force -ErrorAction SilentlyContinue
                Write-Log "Stopped [$process]"
            }
            Start-Sleep -Seconds 2
        }
        
        # Start each process in the processes to restart array
        foreach ($process in $ProcessesToRestart) {
            $processPath = Join-Path $AppleServicesPath "$process.exe"
            
            if (Test-Path $processPath) {
                Write-Log "Starting [$process]..."
                Start-Process $processPath
                Write-Log "Started [$process] successfully"
                Start-Sleep -Seconds 2
            } else {
                Write-Log "Error: Process executable not found at [$processPath]"
            }
        }

        # Wait for the specified interval
        $waitMessage = "Waiting $IntervalSeconds seconds before cleaning upload directory"
        Write-Log $waitMessage
        Start-Sleep -Seconds $IntervalSeconds
        
        # Delete files from upload directory if enabled
        if ($DeleteAfterUpload -and (Test-Path $UploadDirectory)) {
            $deletedCount = 0
            $photos = Get-ChildItem $UploadDirectory -Recurse -File
            
            foreach ($photo in $photos) {
                try {
                    $photoPath = $photo.FullName
                    Remove-Item -Path $photoPath -Force
                    Write-Log "Deleted [$photoPath]"
                    $deletedCount++
                } catch {
                    Write-Log "Failed to delete [$($photo.FullName)]: $($_.Exception.Message)"
                }
            }
            
            Write-Log "Deleted $deletedCount files from upload directory"
        }
        
        Write-Log "Processing cycle completed"
    }
} catch {
    Write-Log "Script error: $($_.Exception.Message)"
    exit 1
} finally {
    Write-Log "iCloud upload management service stopped"
} 