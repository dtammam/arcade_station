@echo on
REM Debug version of the iCloud manager batch file - shows all output for troubleshooting

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
echo Script directory: %SCRIPT_DIR%

REM Create a temporary PowerShell script to read config and launch the main script
set "TEMP_SCRIPT=%TEMP%\debug_icloud_helper.ps1"
echo Creating helper script at: %TEMP_SCRIPT%

echo $configPath = Join-Path $pwd.Path 'config\screenshot_config.toml' > "%TEMP_SCRIPT%"
echo Write-Host "Looking for config at: $configPath" >> "%TEMP_SCRIPT%"
echo if (-not (Test-Path $configPath)) { >> "%TEMP_SCRIPT%"
echo     Write-Host "Config file not found at: $configPath" >> "%TEMP_SCRIPT%"
echo     exit 1 >> "%TEMP_SCRIPT%"
echo } >> "%TEMP_SCRIPT%"
echo. >> "%TEMP_SCRIPT%"
echo try { >> "%TEMP_SCRIPT%"
echo     $config = Get-Content $configPath -Raw >> "%TEMP_SCRIPT%"
echo     Write-Host "Config file loaded successfully" >> "%TEMP_SCRIPT%"
echo     if ($config -match '\[icloud_upload\](.*?)(\[|$)') { >> "%TEMP_SCRIPT%"
echo         Write-Host "Found icloud_upload section in config" >> "%TEMP_SCRIPT%"
echo         $section = $matches[1] >> "%TEMP_SCRIPT%"
echo. >> "%TEMP_SCRIPT%"
echo         # Extract parameters from config >> "%TEMP_SCRIPT%"
echo         $applePath = if ($section -match 'apple_services_path\s*=\s*"([^"]*)"') { $matches[1] } else { "C:\Program Files (x86)\Common Files\Apple\Internet Services\" } >> "%TEMP_SCRIPT%"
echo         $uploadDir = if ($section -match 'upload_directory\s*=\s*"([^"]*)"') { $matches[1] } else { "C:\Users\me\Pictures\Uploads" } >> "%TEMP_SCRIPT%"
echo         $interval = if ($section -match 'interval_seconds\s*=\s*(\d+)') { $matches[1] } else { 360 } >> "%TEMP_SCRIPT%"
echo. >> "%TEMP_SCRIPT%"
echo         # Get processes to restart >> "%TEMP_SCRIPT%"
echo         $processesArray = @() >> "%TEMP_SCRIPT%"
echo         if ($section -match 'processes_to_restart\s*=\s*\[(.*?)\]') { >> "%TEMP_SCRIPT%"
echo             $processesList = $matches[1] >> "%TEMP_SCRIPT%"
echo             Write-Host "Found processes list: $processesList" >> "%TEMP_SCRIPT%"
echo             $processesList -split ',' | ForEach-Object { >> "%TEMP_SCRIPT%"
echo                 if ($_ -match '"([^"]*)"') { >> "%TEMP_SCRIPT%"
echo                     $processesArray += $matches[1] >> "%TEMP_SCRIPT%"
echo                     Write-Host "Added process: $($matches[1])" >> "%TEMP_SCRIPT%"
echo                 } >> "%TEMP_SCRIPT%"
echo             } >> "%TEMP_SCRIPT%"
echo         } >> "%TEMP_SCRIPT%"
echo. >> "%TEMP_SCRIPT%"
echo         # Default to these processes if none specified >> "%TEMP_SCRIPT%"
echo         if ($processesArray.Count -eq 0) { >> "%TEMP_SCRIPT%"
echo             Write-Host "No processes found in config, using defaults" >> "%TEMP_SCRIPT%"
echo             $processesArray = @("iCloudServices", "iCloudPhotos") >> "%TEMP_SCRIPT%"
echo         } >> "%TEMP_SCRIPT%"
echo. >> "%TEMP_SCRIPT%"
echo         # Launch the main script >> "%TEMP_SCRIPT%"
echo         $mainScript = "%SCRIPT_DIR%\manage_icloud_uploads.ps1" >> "%TEMP_SCRIPT%"
echo         Write-Host "Main script path: $mainScript" >> "%TEMP_SCRIPT%"
echo         Write-Host "Launching main script with parameters:" >> "%TEMP_SCRIPT%"
echo         Write-Host "- AppleServicesPath: $applePath" >> "%TEMP_SCRIPT%"
echo         Write-Host "- ProcessesToRestart: $processesArray" >> "%TEMP_SCRIPT%"
echo         Write-Host "- UploadDirectory: $uploadDir" >> "%TEMP_SCRIPT%"
echo         Write-Host "- IntervalSeconds: $interval" >> "%TEMP_SCRIPT%"
echo. >> "%TEMP_SCRIPT%"
echo         # Execute the script with parameters >> "%TEMP_SCRIPT%"
echo         & $mainScript -AppleServicesPath $applePath -ProcessesToRestart $processesArray -UploadDirectory $uploadDir -IntervalSeconds $interval -DeleteAfterUpload $true >> "%TEMP_SCRIPT%"
echo     } else { >> "%TEMP_SCRIPT%"
echo         Write-Host "icloud_upload section not found in config file" >> "%TEMP_SCRIPT%"
echo         exit 1 >> "%TEMP_SCRIPT%"
echo     } >> "%TEMP_SCRIPT%"
echo } catch { >> "%TEMP_SCRIPT%"
echo     Write-Host "Error processing config: $_" >> "%TEMP_SCRIPT%"
echo     Write-Host $_.Exception.Message >> "%TEMP_SCRIPT%"
echo     Write-Host $_.ScriptStackTrace >> "%TEMP_SCRIPT%"
echo     exit 1 >> "%TEMP_SCRIPT%"
echo } >> "%TEMP_SCRIPT%"

REM Run the helper script in a visible window with output
echo Running PowerShell helper script...
powershell.exe -ExecutionPolicy Bypass -NoProfile -File "%TEMP_SCRIPT%"

echo.
echo If you don't see any errors above, the script is running.
echo Press any key to close this window (the iCloud manager will continue running)
pause 