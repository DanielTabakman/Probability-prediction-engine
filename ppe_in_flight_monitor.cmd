@echo off
setlocal
REM Adaptive VM in-flight monitor — mirror-first; escalate when stuck.
REM   ppe_in_flight_monitor.cmd              one pass (agent loop)
REM   ppe_in_flight_monitor.cmd --daemon     poll until phase clears
REM   ppe_in_flight_monitor.cmd --json       machine-readable pass

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_no_loop.local.cmd" call "%CD%\ppe_operator_no_loop.local.cmd"

python "%CD%\scripts\ppe_in_flight_monitor.py" --repo-root "%CD%" %*
exit /b %ERRORLEVEL%
