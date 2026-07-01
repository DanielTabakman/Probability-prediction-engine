@echo off
setlocal
REM VM loop-host weekly hygiene — worktree detach + git heal + ensure stack.
REM Usage: VM_HYGIENE.cmd [--quiet]

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_loop_host.local.cmd" call "%CD%\ppe_operator_loop_host.local.cmd"
if exist "%CD%\call_ppe_operator_local.cmd" call "%CD%\call_ppe_operator_local.cmd"
set "PPE_OPERATOR_PROFILE=local"
set "PPE_SKIP_ACP=1"
set "PPE_STACK_HEADLESS=1"

python "%CD%\scripts\ppe_operator_env.py"
if errorlevel 1 exit /b 1

python "%CD%\scripts\ppe_vm_bootstrap.py" --repo-root "%CD%" --no-sync --no-queue-repair --ensure-stack
set "RC=%ERRORLEVEL%"

call "%CD%\check_vm_loop.cmd" --no-pause
if errorlevel 1 set "RC=1"

if /i "%~1"=="--quiet" exit /b %RC%
echo.
echo [VM_HYGIENE] done exit=%RC%
pause
exit /b %RC%
