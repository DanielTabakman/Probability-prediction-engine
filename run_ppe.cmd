@echo off
setlocal enabledelayedexpansion

REM Unified PPE entry: full relay phase from ACTIVE_PHASE_MANIFEST.json (default).
REM Usage:
REM   run_ppe.cmd
REM   run_ppe.cmd --dry-run
REM   run_ppe.cmd --status
REM   run_ppe.cmd --plan docs/SOP/PHASE_PLANS/<plan>.json
REM   run_ppe.cmd --slice <sliceId>

set "REPO_ROOT=%~dp0"
set "REPO_ROOT=%REPO_ROOT:~0,-1%"

set "PYTHONPATH=%REPO_ROOT%"
python "%REPO_ROOT%\scripts\ppe_run.py" --repo-root "%REPO_ROOT%" %*
set "EXIT_CODE=%ERRORLEVEL%"
exit /b %EXIT_CODE%
