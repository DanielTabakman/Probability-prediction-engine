@echo off
setlocal

REM Monday morning pipeline (single Task Scheduler entry):
REM   1. ~06:00 prep — autoclean + easy autofix
REM   2. wait until 08:00 local
REM   3. workflow radar (friction scan, cleanup already done)
REM   4. weekly digest + phone notify
REM Disable toasts: set PPE_NOTIFY=0

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_local.cmd" call "%CD%\ppe_operator_local.cmd"

call "%~dp0monday_morning_prep.cmd" prep
if errorlevel 1 exit /b %ERRORLEVEL%

call "%~dp0monday_morning_prep.cmd" wait
if errorlevel 1 exit /b %ERRORLEVEL%

call "%~dp0token_audit.cmd" --prune-stale
if errorlevel 1 exit /b %ERRORLEVEL%

python "%CD%\scripts\ppe_workflow_radar.py" --repo-root "%CD%" generate --no-cleanup
if errorlevel 1 exit /b %ERRORLEVEL%

call "%~dp0weekly_digest.cmd" generate
if errorlevel 1 exit /b %ERRORLEVEL%

call "%~dp0weekly_digest.cmd" notify
exit /b %ERRORLEVEL%
