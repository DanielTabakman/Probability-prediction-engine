@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\call_ppe_operator_local.cmd" call "%CD%\call_ppe_operator_local.cmd"
python "%CD%\scripts\reset_ntfy_send_state.py" --repo-root "%CD%" %*
exit /b %ERRORLEVEL%
