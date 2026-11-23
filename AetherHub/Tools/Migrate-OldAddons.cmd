@echo off
rem Run once after installing the Aether addons, with WoW closed.
rem Moves settings from CleanBars, MapCoords, PathfinderMap and QuarryMarks to their Aether names.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Migrate-OldAddons.ps1"
pause
