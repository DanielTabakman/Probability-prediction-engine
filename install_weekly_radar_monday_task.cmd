@echo off
setlocal

REM Register Task Scheduler: Monday 04:00 workflow radar + weekly digest + notify.
REM Run once from repo root.

cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\scripts\install_weekly_radar_task.ps1" -RepoRoot "%CD%" %*
exit /b %ERRORLEVEL%
