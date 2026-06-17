@echo off
REM === VM ONLY — double-click this file in File Explorer ===
REM Shows operator status. Window stays open until you press a key.

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_loop_host.local.cmd" call "%CD%\ppe_operator_loop_host.local.cmd"
if exist "%CD%\call_ppe_operator_local.cmd" call "%CD%\call_ppe_operator_local.cmd"
set "PPE_OPERATOR_PROFILE=local"
set "PPE_STACK_HEADLESS=1"

echo [VM_STATUS] repo=%CD%
echo [VM_STATUS] PPE_LOOP_HOST=%PPE_LOOP_HOST%
echo [VM_STATUS] PPE_STACK_HEADLESS=%PPE_STACK_HEADLESS%
echo.
echo [VM_STATUS] Loading... please wait about 10 seconds.
echo.

python "%CD%\scripts\ppe_operator_env.py"
if errorlevel 1 goto done

python -u "%CD%\scripts\ppe_autobuilder.py" --repo-root "%CD%" status --brief
set "RC=%ERRORLEVEL%"

:done
echo.
echo ============================================================
echo  Look for the PHASE= line above. Copy it if you need help.
echo ============================================================
echo.
echo Press any key to close...
pause >nul
exit /b %RC%
