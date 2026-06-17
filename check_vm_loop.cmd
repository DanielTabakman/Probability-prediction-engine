@echo off
setlocal
REM Quick VM health check (no manual set commands).
REM Win+R:  C:\Users\ppeloop\Probability-prediction-engine\check_vm_loop.cmd

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_loop_host.local.cmd" call "%CD%\ppe_operator_loop_host.local.cmd"
if exist "%CD%\call_ppe_operator_local.cmd" call "%CD%\call_ppe_operator_local.cmd"
set "PPE_OPERATOR_PROFILE=local"

echo [check_vm_loop] repo=%CD%
echo [check_vm_loop] PPE_LOOP_HOST=%PPE_LOOP_HOST%
echo [check_vm_loop] PPE_STACK_HEADLESS=%PPE_STACK_HEADLESS%
echo.

call "%CD%\ppe_autobuilder.cmd" status --brief
set "RC=%ERRORLEVEL%"

echo.
if /i "%~1"=="--no-pause" exit /b %RC%
echo Press any key to close this window...
pause >nul
exit /b %RC%
