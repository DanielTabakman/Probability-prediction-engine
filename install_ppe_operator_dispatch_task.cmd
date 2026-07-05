@echo off
setlocal
REM Install Task Scheduler job: ppe_operator_dispatch every 15m (opt-in desktop only).
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\scripts\install_ppe_operator_dispatch_task.ps1" -RepoRoot "%CD%" %*
exit /b %ERRORLEVEL%
