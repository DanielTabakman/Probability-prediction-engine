@echo off
setlocal
REM VM loop-host one-shot bootstrap: config, git hygiene, slice sync, optional relay + stack.
REM Usage:
REM   vm_bootstrap.cmd              diagnose + sync (safe, no relay)
REM   vm_bootstrap.cmd --recover    sync + run_ppe_local if RUN_LOCAL + start headless stack
REM   vm_bootstrap.cmd --check      status only after setup
REM See docs/SOP/PPE_VM_LOOP_HOST_V1.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_loop_host.local.cmd" call "%CD%\ppe_operator_loop_host.local.cmd"
if exist "%CD%\call_ppe_operator_local.cmd" call "%CD%\call_ppe_operator_local.cmd"
set "PPE_OPERATOR_PROFILE=local"
set "PPE_SKIP_ACP=1"
set "PPE_STACK_HEADLESS=1"

python "%CD%\scripts\ppe_operator_env.py"
if errorlevel 1 exit /b 1

set "EXTRA="
set "PASSTHRU=%*"
if /i "%~1"=="--recover" (
  set "EXTRA=--run-local --ensure-stack"
  set "PASSTHRU="
  shift
)
if /i "%~1"=="--check" (
  call "%CD%\check_vm_loop.cmd"
  exit /b %ERRORLEVEL%
)

python "%CD%\scripts\ppe_vm_bootstrap.py" --repo-root "%CD%" %EXTRA% %PASSTHRU%
set "RC=%ERRORLEVEL%"
if /i "%~1"=="--recover" (
  echo.
  echo [vm_bootstrap] waiting for detached run_ppe_local if started...
  timeout /t 5 /nobreak >nul
)
call "%CD%\ppe_autobuilder.cmd" status --brief
exit /b %RC%
