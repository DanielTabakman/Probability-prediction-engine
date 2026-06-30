@echo off
setlocal

REM Unified tracking status — factory + validation + steering + assets + trader outcomes.
REM Usage:
REM   ppe_tracking_status.cmd
REM   ppe_tracking_status.cmd --brief
REM   ppe_tracking_status.cmd --json --days 14

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\ppe_tracking_status.py" --repo-root "%CD%" %*
exit /b %ERRORLEVEL%
