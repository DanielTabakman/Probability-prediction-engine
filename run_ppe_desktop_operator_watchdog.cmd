@echo off
setlocal

REM Quiet background ensure: git pull + restart loop/watch if missing.
REM Intended for Task Scheduler (hidden, every ~15 min). See install_ppe_desktop_operator_watchdog_task.cmd.

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_local.cmd" call "%CD%\ppe_operator_local.cmd"
set "PPE_OPERATOR_PROFILE=local"
set "PPE_SKIP_ACP=1"
set "PPE_WORKER_MODE=deterministic"

python "%CD%\scripts\ppe_operator_env.py" >nul 2>&1
if errorlevel 1 exit /b 1

python "%CD%\scripts\ppe_operator_git_sync.py" --repo-root "%CD%" --pull >nul 2>&1
python "%CD%\scripts\ppe_desktop_operator_stack.py" --repo-root "%CD%" --ensure --no-propagate
exit /b %ERRORLEVEL%
