@echo off
rem Turns off the automatic background refresh.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Update-PathfinderData.ps1" -RemoveSchedule
pause
