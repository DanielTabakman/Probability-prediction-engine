@echo off
setlocal

REM Desktop operator stack: auto-loop + mobile watch (two terminals).
REM Run on the always-on PC. See docs/SOP/PPE_MOBILE_OPERATOR_V1.md

cd /d "%~dp0"

if exist "%CD%\ppe_operator_local.cmd" call "%CD%\ppe_operator_local.cmd"

start "PPE auto loop" cmd /k call "%~dp0run_ppe_auto_local_loop.cmd"
timeout /t 3 /nobreak >nul
start "PPE mobile watch" cmd /k call "%~dp0watch_operator_mobile.cmd"

echo Started:
echo   1. PPE auto loop
echo   2. PPE mobile watch
echo.
echo Set PPE_NTFY_TOPIC before first run (see docs/SOP/PPE_MOBILE_OPERATOR_V1.md).
exit /b 0
