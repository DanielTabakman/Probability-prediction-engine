@echo off
setlocal enabledelayedexpansion

REM Run one product slice via agent-cli (explicit Cursor billing).
REM Does NOT apply PPE_AUTO_OPERATOR skip-ACP (set PPE_OPERATOR_ENV_APPLIED).
REM
REM Usage:
REM   run_product_slice.cmd <sliceId> [phasePlanPath]
REM
REM phasePlanPath defaults to ACTIVE_PHASE_MANIFEST.json phasePlanPath when omitted.

set "REPO_ROOT=%~dp0"
set "REPO_ROOT=%REPO_ROOT:~0,-1%"
set "PYTHONPATH=%REPO_ROOT%"
set "PPE_OPERATOR_ENV_APPLIED=1"

set "SLICE_ID=%~1"
if "%SLICE_ID%"=="" (
  echo usage: run_product_slice.cmd ^<sliceId^> [phasePlanPath]
  exit /b 2
)

set "PLAN_ARG=%~2"
if "%PLAN_ARG%"=="" (
  python "%REPO_ROOT%\scripts\ppe_run_product_slice.py" --repo-root "%REPO_ROOT%" --slice-id "%SLICE_ID%"
) else (
  python "%REPO_ROOT%\scripts\ppe_run_product_slice.py" --repo-root "%REPO_ROOT%" --slice-id "%SLICE_ID%" --plan "%PLAN_ARG%"
)
exit /b %ERRORLEVEL%
