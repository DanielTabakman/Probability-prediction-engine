@echo off
setlocal

REM Steward Mon/Thu nudge — human commitments (separate ntfy topic).
REM Usage: steward_nudge.cmd [monday|thursday|auto]

cd /d "%~dp0"
if exist "%~dp0ppe_operator_local.cmd" call "%~dp0ppe_operator_local.cmd"
if exist "%~dp0ppe_operator_notify.local.cmd" call "%~dp0ppe_operator_notify.local.cmd"

set "SLOT=auto"
if not "%~1"=="" set "SLOT=%~1"

python "%~dp0scripts\ppe_steward_nudge.py" --repo-root "%CD%" --slot %SLOT%
exit /b %ERRORLEVEL%
