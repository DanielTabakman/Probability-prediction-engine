@echo off
setlocal
REM === DESKTOP ONLY — live VM loop status (auto-ensure stack when down) ===
REM Agent/non-interactive: DESKTOP_VM_STATUS.cmd --no-pause

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_no_loop.local.cmd" call "%CD%\ppe_operator_no_loop.local.cmd"
set "PPE_OPERATOR_PROFILE=local"

python "%CD%\scripts\ppe_desktop_vm_status.py" --repo-root "%CD%"
set "RC=%ERRORLEVEL%"

if /i "%~1"=="--no-pause" exit /b %RC%
echo.
pause
exit /b %RC%
