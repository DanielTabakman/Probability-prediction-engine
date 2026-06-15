@echo off
setlocal

REM Headless desktop operator stack — one terminal, detached workers, log files only.
REM Usage:
REM   run_ppe_headless_stack.cmd            (foreground supervisor — Ctrl+C to stop)
REM   run_ppe_headless_stack.cmd --ensure   (start detached supervisor if not running)
REM   run_ppe_headless_stack.cmd --stop     (stop supervisor + workers)
REM See docs/SOP/PPE_HEADLESS_STACK_V1.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
set "PPE_STACK_HEADLESS=1"

call "%CD%\call_ppe_operator_local.cmd"
set "PPE_OPERATOR_PROFILE=local"

python "%CD%\scripts\ppe_operator_env.py"
if errorlevel 1 exit /b 1

if /i not "%~1"=="--stop" (
  python "%CD%\scripts\ppe_loop_host_guard.py" --require
  if errorlevel 1 exit /b %ERRORLEVEL%
)

if /i "%~1"=="--ensure" (
  python "%CD%\scripts\ppe_headless_stack_supervisor.py" --repo-root "%CD%" --ensure
  exit /b %ERRORLEVEL%
)

if /i "%~1"=="--stop" (
  python "%CD%\scripts\ppe_headless_stack_supervisor.py" --repo-root "%CD%" --stop
  exit /b %ERRORLEVEL%
)

python "%CD%\scripts\ppe_headless_stack_supervisor.py" --repo-root "%CD%"
exit /b %ERRORLEVEL%
