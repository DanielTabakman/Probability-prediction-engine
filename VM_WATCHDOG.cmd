@echo off
setlocal
REM VM loop host — check stack health; auto-restart if loop down (rate-limited).
REM Optional: schedule every 10 min via Task Scheduler on the VM.

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_loop_host.local.cmd" call "%CD%\ppe_operator_loop_host.local.cmd"
set "PPE_OPERATOR_PROFILE=local"
set "PPE_SKIP_ACP=1"
set "PPE_STACK_HEADLESS=1"

python "%CD%\scripts\ppe_vm_watchdog.py" --repo-root "%CD%" %*
set "RC=%ERRORLEVEL%"
if /i not "%~1"=="--quiet" pause
exit /b %RC%
