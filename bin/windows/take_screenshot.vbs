' VBScript to take a screenshot with absolutely no visible window
' This will not show any console or take focus from the current application

' Set paths
pythonwPath = "C:\Repositories\arcade_station\.venv\Scripts\pythonw.exe"
scriptPath = "C:\Repositories\arcade_station\src\arcade_station\core\common\monitor_screenshot.py"

' Create a Windows Shell object
Set objShell = CreateObject("WScript.Shell")

' Run pythonw.exe with the screenshot script in a completely hidden way
' 0 = Hide the window and activate another window
objShell.Run Chr(34) & pythonwPath & Chr(34) & " " & Chr(34) & scriptPath & Chr(34), 0, False

' Exit immediately
Set objShell = Nothing 