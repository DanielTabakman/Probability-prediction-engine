@echo off
setlocal

REM Register Task Scheduler: Monday weekly digest + phone ntfy push.
REM Run once from repo root.

cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\scripts\install_weekly_digest_task.ps1" -RepoRoot "%CD%" %*
exit /b %ERRORLEVEL%
