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
REM Optional SELECTION automation: if no plan is selected, pick from docs/SOP/PHASE_QUEUE.json.
REM This is safe: it will not override READY/RUNNING manifests.
REM If selection fails, print the selector output so the operator can see why.
set "SELECT_ONLY=0"
if /i "%~1"=="--select-only" set "SELECT_ONLY=1"
if /i "%~1"=="--select-only" shift

set "SEL_OUT=%TEMP%\ppe_auto_select_%RANDOM%.json"
if "%SELECT_ONLY%"=="1" (
  python "%REPO_ROOT%\scripts\ppe_auto_select.py" --repo-root "%REPO_ROOT%" --select-only > "%SEL_OUT%" 2>&1
) else (
  python "%REPO_ROOT%\scripts\ppe_auto_select.py" --repo-root "%REPO_ROOT%" --apply > "%SEL_OUT%" 2>&1
)
set "SEL_RC=%ERRORLEVEL%"
if not "%SEL_RC%"=="0" (
  type "%SEL_OUT%"
)
del "%SEL_OUT%" >nul 2>nul
if "%SELECT_ONLY%"=="1" exit /b %SEL_RC%

python "%REPO_ROOT%\scripts\ppe_run.py" --repo-root "%REPO_ROOT%" %*
set "EXIT_CODE=%ERRORLEVEL%"
exit /b %EXIT_CODE%
