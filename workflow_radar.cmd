@echo off
setlocal

REM Weekly workflow radar (friction signals + orphan cleanup).
REM Usage:
REM   workflow_radar.cmd generate
REM   workflow_radar.cmd generate --week 2026-06-08
REM   workflow_radar.cmd cleanup
REM   workflow_radar.cmd cleanup --dry-run

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_local.cmd" call "%CD%\ppe_operator_local.cmd"

python "%CD%\scripts\ppe_workflow_radar.py" --repo-root "%CD%" %*
exit /b %ERRORLEVEL%
