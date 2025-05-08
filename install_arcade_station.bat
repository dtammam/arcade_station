@echo off
echo Attempting to run installer script with PowerShell...
powershell -ExecutionPolicy Bypass -NoProfile -NonInteractive -File "%~dp0install_logic.ps1"
if %ERRORLEVEL% neq 0 (
    echo Script finished with errors or was cancelled.
) else (
    echo Script finished successfully.
)
echo.
pause
exit /b %ERRORLEVEL%