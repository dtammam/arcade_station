@echo on
REM Kill the iCloud manager PowerShell script if it's running

echo Stopping iCloud management processes...

REM Kill any running instances of the main PowerShell script
powershell -Command "Get-Process -Name powershell | Where-Object { $_.CommandLine -like '*manage_icloud_uploads.ps1*' } | ForEach-Object { Write-Host ('Killing process: ' + $_.Id); Stop-Process -Id $_.Id -Force }"

REM Kill any helper scripts
powershell -Command "Get-Process -Name powershell | Where-Object { $_.CommandLine -like '*icloud_helper.ps1*' } | ForEach-Object { Write-Host ('Killing process: ' + $_.Id); Stop-Process -Id $_.Id -Force }"

REM Restart Apple services manually if needed
echo.
echo Do you want to restart Apple iCloud services manually? (Y/N)
choice /C YN /M "Restart services:"
if %ERRORLEVEL% EQU 1 (
  echo Restarting iCloud services...
  taskkill /F /IM iCloudServices.exe 2>nul
  taskkill /F /IM iCloudPhotos.exe 2>nul
  
  timeout /t 2 /nobreak >nul
  
  set "APPLE_PATH=C:\Program Files (x86)\Common Files\Apple\Internet Services"
  if exist "%APPLE_PATH%\iCloudServices.exe" (
    start "" "%APPLE_PATH%\iCloudServices.exe"
    echo Started iCloudServices
  )
  if exist "%APPLE_PATH%\iCloudPhotos.exe" (
    start "" "%APPLE_PATH%\iCloudPhotos.exe"
    echo Started iCloudPhotos
  )
)

echo.
echo Process complete. Press any key to exit.
pause 