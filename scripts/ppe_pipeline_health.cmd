@echo off
REM Founder pipeline diagnostics — root cause, milestone clock, regression ntfy.
setlocal
cd /d "%~dp0\.."
if exist "%CD%\ppe_operator_notify.local.cmd" call "%CD%\ppe_operator_notify.local.cmd"
set "PYTHONPATH=%CD%"
python "%CD%\scripts\ppe_pipeline_health.py" --write %*
exit /b %ERRORLEVEL%
