@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_local.cmd" call "%CD%\ppe_operator_local.cmd"
if not defined PPE_NTFY_CMD_SSE set "PPE_NTFY_CMD_SSE=1"
python "%CD%\scripts\ppe_ntfy_listen.py" --repo-root "%CD%"
exit /b %ERRORLEVEL%
