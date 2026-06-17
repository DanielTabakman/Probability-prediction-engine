@echo off
setlocal
REM VM loop host — schedule VM_WATCHDOG.cmd every 10 minutes.

cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\scripts\install_ppe_vm_watchdog_task.ps1" -RepoRoot "%CD%"
pause
exit /b %ERRORLEVEL%
