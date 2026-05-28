@echo off
setlocal enabledelayedexpansion

REM Unified PPE entry: full relay phase from ACTIVE_PHASE_MANIFEST.json (default).
REM Usage:
REM   run_ppe.cmd
REM   run_ppe.cmd --dry-run
REM   run_ppe.cmd --status
REM   run_ppe.cmd --continuous
REM   run_ppe.cmd --plan docs/SOP/PHASE_PLANS/<plan>.json
REM   run_ppe.cmd --slice <sliceId>

set "REPO_ROOT=%~dp0"
set "REPO_ROOT=%REPO_ROOT:~0,-1%"

set "PYTHONPATH=%REPO_ROOT%"
if not defined PPE_WORKER_MODE if "%PPE_SKIP_ACP%"=="1" set "PPE_WORKER_MODE=deterministic"
set "CONTINUOUS=0"
set "SELECT_ONLY=0"

:strip_flags
if "%~1"=="" goto strip_done
if /i "%~1"=="--continuous" (
  set "CONTINUOUS=1"
  shift
  goto strip_flags
)
if /i "%~1"=="--select-only" (
  set "SELECT_ONLY=1"
  shift
  goto strip_flags
)
goto strip_done

:strip_done
REM SELECTION: roadmap bootstrap (if idle), finalize COMPLETE+stale plan, select next READY.
set "SEL_OUT=%TEMP%\ppe_auto_select_%RANDOM%.json"
if "%SELECT_ONLY%"=="1" (
  python "%REPO_ROOT%\scripts\ppe_auto_select.py" --repo-root "%REPO_ROOT%" --select-only > "%SEL_OUT%" 2>&1
) else (
  python "%REPO_ROOT%\scripts\ppe_auto_select.py" --repo-root "%REPO_ROOT%" --apply > "%SEL_OUT%" 2>&1
)
set "SEL_RC=%ERRORLEVEL%"
type "%SEL_OUT%"
del "%SEL_OUT%" >nul 2>nul
if "%SELECT_ONLY%"=="1" exit /b %SEL_RC%
if not "%SEL_RC%"=="0" exit /b %SEL_RC%

if "%CONTINUOUS%"=="1" (
  python "%REPO_ROOT%\scripts\ppe_run.py" --repo-root "%REPO_ROOT%" --continuous %*
  exit /b %ERRORLEVEL%
)

python "%REPO_ROOT%\scripts\ppe_run.py" --repo-root "%REPO_ROOT%" %*
exit /b %ERRORLEVEL%
