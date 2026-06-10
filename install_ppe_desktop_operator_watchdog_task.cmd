@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install_ppe_desktop_operator_watchdog_task.ps1" -RepoRoot "%CD%" %*
exit /b %ERRORLEVEL%
