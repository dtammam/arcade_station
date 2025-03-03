@echo off
REM Hide console window completely
if not "%1"=="hidden" start /b /min cmd /c %0 hidden & exit
REM Run the screenshot script without showing a window
start /b "Screenshot" "C:\Repositories\arcade_station\.venv\Scripts\pythonw.exe" "C:\Repositories\arcade_station\src\arcade_station\screenshot.py" 