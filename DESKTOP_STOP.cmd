@echo off
REM === DESKTOP ONLY — double-click in File Explorer ===
REM Stops operator popups on your daily PC. Loop belongs on the VM.

cd /d "%~dp0"
call "%~dp0fix_desktop_stop_all.cmd"
echo.
echo ============================================================
echo  Desktop operator stopped. Use Cursor here for IDE BUILD only.
echo  The loop runs on the Hyper-V VM, not this PC.
echo ============================================================
echo.
pause
