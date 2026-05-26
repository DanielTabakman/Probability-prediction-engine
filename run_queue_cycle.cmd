@echo off
setlocal enabledelayedexpansion

REM Chapter queue cycle: pop PENDING chapter, write plan+manifest, run_ppe.cmd.
REM Usage:
REM   run_queue_cycle.cmd
REM   run_queue_cycle.cmd --dry-run
REM   run_queue_cycle.cmd --max-chapters 3 --continuous

set "REPO_ROOT=%~dp0"
set "REPO_ROOT=%REPO_ROOT:~0,-1%"
set "PYTHONPATH=%REPO_ROOT%"

python "%REPO_ROOT%\scripts\run_queue_cycle.py" --repo-root "%REPO_ROOT%" %*
exit /b %ERRORLEVEL%
