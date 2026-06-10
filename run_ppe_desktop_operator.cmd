@echo off
setlocal

REM Single desktop operator entry: git pull, build queue, ensure loop+watch stack.
REM Task Scheduler at logon should call this (see install_ppe_desktop_operator_task.cmd).
REM Usage:
REM   run_ppe_desktop_operator.cmd
REM   run_ppe_desktop_operator.cmd --status
REM   run_ppe_desktop_operator.cmd --json

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

if exist "%CD%\ppe_operator_local.cmd" call "%CD%\ppe_operator_local.cmd"
set "PPE_OPERATOR_PROFILE=local"
set "PPE_SKIP_ACP=1"
set "PPE_WORKER_MODE=deterministic"

python "%CD%\scripts\ppe_operator_env.py"
if errorlevel 1 exit /b 1

echo [run_ppe_desktop_operator] git sync pull
python "%CD%\scripts\ppe_operator_git_sync.py" --repo-root "%CD%" --pull

echo [run_ppe_desktop_operator] queue propagate + stack ensure
if "%~1"=="" (
  python "%CD%\scripts\ppe_desktop_operator_stack.py" --repo-root "%CD%" --ensure
) else (
  python "%CD%\scripts\ppe_desktop_operator_stack.py" --repo-root "%CD%" %*
)
set "RC=%ERRORLEVEL%"

echo.
echo Phone triage: run_ppe_operator.cmd --brief
exit /b %RC%
