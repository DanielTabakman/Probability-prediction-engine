@echo off
REM Install Desktop shortcuts on the correct machine (VM vs daily PC).
REM Usually called automatically from VM_UPDATE / VM_START / DESKTOP_BUILD — not by hand.

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_loop_host.local.cmd" call "%CD%\ppe_operator_loop_host.local.cmd"
if exist "%CD%\ppe_operator_no_loop.local.cmd" call "%CD%\ppe_operator_no_loop.local.cmd"

python "%CD%\scripts\ppe_operator_shortcuts.py" --repo-root "%CD%" --apply %*
set "RC=%ERRORLEVEL%"

if /i "%~1"=="--no-pause" exit /b %RC%
if /i "%~1"=="--quiet" exit /b %RC%
if /i "%~2"=="--no-pause" exit /b %RC%
if /i "%~2"=="--quiet" exit /b %RC%
pause
exit /b %RC%
