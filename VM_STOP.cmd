@echo off
REM === VM ONLY — double-click this file in File Explorer ===
REM Stops all operator popups. Window stays open so you can read it.

cd /d "%~dp0"
call "%~dp0fix_vm_stop_all.cmd"
echo.
echo ============================================================
echo  STOP complete. Close any blank cmd windows by hand (click X).
echo  Do NOT run START until popups are gone.
echo ============================================================
echo.
pause
