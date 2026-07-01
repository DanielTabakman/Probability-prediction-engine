@echo off
REM One-shot infra doctor — SSH, gh, ntfy, mirror blind spots (not autobuilder).
setlocal
cd /d "%~dp0\.."
if exist "%CD%\ppe_operator_notify.local.cmd" call "%CD%\ppe_operator_notify.local.cmd"
if exist "%CD%\ppe_operator_no_loop.local.cmd" call "%CD%\ppe_operator_no_loop.local.cmd"
set "PYTHONPATH=%CD%"
python "%CD%\scripts\ppe_operator_doctor.py" %*
exit /b %ERRORLEVEL%
