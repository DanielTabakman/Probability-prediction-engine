@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_no_loop.local.cmd" call "%CD%\ppe_operator_no_loop.local.cmd"
python "%CD%\scripts\ppe_operator_stuck_run_local.py" --ensure-watch --repo-root "%CD%"
exit /b %ERRORLEVEL%
