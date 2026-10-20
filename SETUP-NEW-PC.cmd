@echo off
REM Double-click this file to open the beginner setup menu (Windows).
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup-new-pc.ps1" menu
pause
