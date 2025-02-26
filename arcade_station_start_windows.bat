@echo off
REM This is a wrapper script that calls the platform-specific script

set "SCRIPT_DIR=%~dp0"
cd "%SCRIPT_DIR%"

REM Call the Windows-specific script with the same arguments
call src\arcade_station\core\windows\arcade_station_start.bat %* 