@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\call_ppe_operator_local.cmd" call "%CD%\call_ppe_operator_local.cmd"
python "%CD%\scripts\ppe_ntfy_phone_diag.py" --heal-vm %*
exit /b %ERRORLEVEL%
