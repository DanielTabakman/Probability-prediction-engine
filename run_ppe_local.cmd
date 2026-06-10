@echo off
setlocal enabledelayedexpansion

REM Single chapter / phase run with local profile (no ACP). Use after IDE product BUILD.
REM Optional: mark_ide_product_ready.cmd <sliceId> [phasePlanPath] before this run.
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_local.cmd" call "%CD%\ppe_operator_local.cmd"
set "PPE_OPERATOR_PROFILE=local"
set "PPE_SKIP_ACP=1"
set "PPE_WORKER_MODE=deterministic"

python "%CD%\scripts\ppe_operator_env.py"
if errorlevel 1 exit /b 1

python "%CD%\scripts\ppe_operator_git_sync.py" --repo-root "%CD%" --pull

call "%CD%\run_ppe.cmd" %*
set "RC=%ERRORLEVEL%"
if "%RC%"=="0" (
  python -c "from pathlib import Path; from scripts.ppe_manifest import load_manifest; m=load_manifest(Path('.')); import sys; sys.exit(0 if str(m.get('status') or '').upper()=='COMPLETE' else 1)" >nul 2>&1
  if not errorlevel 1 (
    python "%CD%\scripts\ppe_ide_product_ready.py" --repo-root "%CD%" --clear >nul 2>&1
  )
  python "%CD%\scripts\ppe_operator_git_sync.py" --repo-root "%CD%" --publish
)
exit /b %RC%
