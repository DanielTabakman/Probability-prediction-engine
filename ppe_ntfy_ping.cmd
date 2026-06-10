@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_local.cmd" call "%CD%\ppe_operator_local.cmd"
python "%CD%\scripts\ppe_ntfy_ping.py"
exit /b %ERRORLEVEL%
