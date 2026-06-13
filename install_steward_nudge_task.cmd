@echo off
setlocal

REM Register Task Scheduler: Mon + Thu steward nudges (human commitments).
REM Run once from repo root. Requires PPE_NTFY_STEWARD_TOPIC in ppe_operator_notify.local.cmd

cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\scripts\install_steward_nudge_task.ps1" -RepoRoot "%CD%" %*
exit /b %ERRORLEVEL%
