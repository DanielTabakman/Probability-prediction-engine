@echo off
REM One-shot infra doctor — SSH, gh, ntfy, mirror blind spots (not autobuilder).
cd /d "%~dp0"
if exist "%~dp0ppe_operator_notify.local.cmd" call "%~dp0ppe_operator_notify.local.cmd"
if exist "%~dp0ppe_operator_no_loop.local.cmd" call "%~dp0ppe_operator_no_loop.local.cmd"
python scripts\ppe_operator_doctor.py %*
exit /b %ERRORLEVEL%
