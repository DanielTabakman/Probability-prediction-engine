@echo off
setlocal
REM Quick VM health check (no manual set commands).
REM Win+R:  C:\Users\ppeloop\Probability-prediction-engine\check_vm_loop.cmd

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_loop_host.local.cmd" call "%CD%\ppe_operator_loop_host.local.cmd"
if exist "%CD%\call_ppe_operator_local.cmd" call "%CD%\call_ppe_operator_local.cmd"
set "PPE_OPERATOR_PROFILE=local"
set "PPE_STACK_HEADLESS=1"

echo [check_vm_loop] repo=%CD%
echo [check_vm_loop] PPE_LOOP_HOST=%PPE_LOOP_HOST%
echo [check_vm_loop] PPE_STACK_HEADLESS=%PPE_STACK_HEADLESS%
echo.

echo [check_vm_loop] Loading... please wait about 10 seconds.
echo.

python "%CD%\scripts\ppe_operator_env.py"
if errorlevel 1 goto done

python -u "%CD%\scripts\ppe_autobuilder.py" --repo-root "%CD%" status --brief
set "RC=%ERRORLEVEL%"

:done
echo.
if /i "%~1"=="--no-pause" exit /b %RC%
echo Press any key to close this window...
pause >nul
exit /b %RC%
