@echo off
rem Double-click to refresh AetherPathfinder's NPC data right now.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Update-PathfinderData.ps1"
pause
