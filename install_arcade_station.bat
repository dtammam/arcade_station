@echo off
:: Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This installer requires administrator privileges.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo Running installer with administrator privileges...
echo Unblocking all files - please wait...
powershell -ExecutionPolicy Bypass -Command "Get-ChildItem -Path '%~dp0' -Recurse | Unblock-File"
powershell -ExecutionPolicy Bypass -NoProfile -NonInteractive -File "%~dp0install_logic.ps1"
if %ERRORLEVEL% neq 0 (
    echo Script finished with errors or was cancelled.
    pause
)
exit /b %ERRORLEVEL%