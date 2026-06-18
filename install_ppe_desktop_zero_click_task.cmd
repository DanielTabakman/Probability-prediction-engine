@echo off
setlocal
REM Register Task Scheduler: zero-click BUILD at user logon (daily PC only).

cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\scripts\install_ppe_desktop_zero_click_task.ps1" -RepoRoot "%CD%"
exit /b %ERRORLEVEL%
