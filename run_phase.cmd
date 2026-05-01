@echo off
setlocal enabledelayedexpansion

REM Thin wrapper: run a phase plan through relay-gated ACP orchestrator + steward autopilot.
REM Usage:
REM   run_phase.cmd <phasePlanPath>

set "REPO_ROOT=%~dp0"
set "REPO_ROOT=%REPO_ROOT:~0,-1%"

set "PLAN_PATH=%~1"
if "%PLAN_PATH%"=="" (
  echo usage: run_phase.cmd ^<phasePlanPath^>
  exit /b 2
)

set "BASELINE_BRANCH=recovery/frontier-steward-v2_1-baseline"

set "ORCH_ROOT=%USERPROFILE%\Desktop\ppe-orchestrator-acp"
if not exist "%ORCH_ROOT%\package.json" (
  set "ORCH_ROOT=%REPO_ROOT%\..\ppe-orchestrator-acp"
)

python "%REPO_ROOT%\scripts\log_event.py" --event-type "run_phase.start" --summary "Start phase plan %PLAN_PATH% (steward)" --actor "wrapper" --ref "kind=cmd,path=run_phase.cmd" --ref "kind=doc,path=%PLAN_PATH%" >nul 2>nul

set "NODE20=%USERPROFILE%\Desktop\ppe-orchestrator-sdk\node\node-v20.18.2-win-x64"
if exist "%NODE20%\npm.cmd" (
  set "PATH=%NODE20%;%PATH%"
)

pushd "%ORCH_ROOT%" >nul
call npm run dev -- run-phase-steward "%REPO_ROOT%" "%PLAN_PATH%" "%BASELINE_BRANCH%"
set "EXIT_CODE=%ERRORLEVEL%"
popd >nul

python "%REPO_ROOT%\scripts\log_event.py" --event-type "run_phase.end" --summary "End phase plan %PLAN_PATH% exit_code=%EXIT_CODE%" --actor "wrapper" --ref "kind=cmd,path=run_phase.cmd" >nul 2>nul

exit /b %EXIT_CODE%

