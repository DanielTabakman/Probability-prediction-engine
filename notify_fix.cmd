@echo off
REM Phone ping when fixing or after fixing a blocked operator state.
REM Requires ppe_operator_notify.local.cmd (PPE_NTFY_TOPIC).

setlocal
set "REPO=%~dp0"
if "%REPO:~-1%"=="\" set "REPO=%REPO:~0,-1%"
if exist "%REPO%\ppe_operator_notify.local.cmd" call "%REPO%\ppe_operator_notify.local.cmd"
python "%REPO%\scripts\ppe_notify_fix.py" %*
