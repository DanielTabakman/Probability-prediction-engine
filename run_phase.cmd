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

set "BASELINE_BRANCH=main"

if /i "%PPE_WORKER_MODE%"=="deterministic" goto local_phase
if "%PPE_SKIP_ACP%"=="1" goto local_phase
if /i "%PPE_USE_LOCAL_PHASE%"=="1" goto local_phase

set "ORCH_ROOT=%USERPROFILE%\Desktop\ppe-orchestrator-acp"
if not exist "%ORCH_ROOT%\package.json" (
  set "ORCH_ROOT=%REPO_ROOT%\..\ppe-orchestrator-acp"
)
if not exist "%ORCH_ROOT%\package.json" (
  set "ORCH_ROOT=%REPO_ROOT%\..\..\..\ppe-orchestrator-acp"
)

python "%REPO_ROOT%\scripts\log_event.py" --event-type "run_phase.start" --summary "Start phase plan %PLAN_PATH% (steward)" --actor "wrapper" --ref "kind=cmd,path=run_phase.cmd" --ref "kind=doc,path=%PLAN_PATH%" >nul 2>nul

set "ACTIVE_RUN=%REPO_ROOT%\\artifacts\\orchestrator\\ACTIVE_RUN.json"
if not exist "%REPO_ROOT%\\artifacts\\orchestrator" (
  mkdir "%REPO_ROOT%\\artifacts\\orchestrator" >nul 2>nul
)
python -c "import json,datetime,pathlib; p=r'%ACTIVE_RUN%'; d={'kind':'phase','plan_path':r'%PLAN_PATH%','baseline_branch':r'%BASELINE_BRANCH%','ts_utc':datetime.datetime.utcnow().replace(microsecond=0).isoformat()+'Z'}; pathlib.Path(p).parent.mkdir(parents=True, exist_ok=True); pathlib.Path(p).write_text(json.dumps(d,indent=2), encoding='utf-8')" >nul 2>nul

set "NODE20=%USERPROFILE%\Desktop\ppe-orchestrator-sdk\node\node-v20.18.2-win-x64"
if exist "%NODE20%\npm.cmd" (
  set "PATH=%NODE20%;%PATH%"
)

pushd "%ORCH_ROOT%" >nul
REM ACP permissions are handled programmatically by the orchestrator; this avoids relying on Cursor popups.
REM Modes: allow-once (default) or allow-always (reduces repeated permission prompts).
set "ACP_PERMISSION_MODE=allow-always"
where npm >nul 2>nul
if "%ERRORLEVEL%"=="0" (
  call npm run dev -- run-phase-steward "%REPO_ROOT%" "%PLAN_PATH%" "%BASELINE_BRANCH%"
) else (
  if exist "%ORCH_ROOT%\\node_modules\\.bin\\tsx.cmd" (
    call "%ORCH_ROOT%\\node_modules\\.bin\\tsx.cmd" src\\cli.ts run-phase-steward "%REPO_ROOT%" "%PLAN_PATH%" "%BASELINE_BRANCH%"
  ) else (
    echo ERROR: npm not found and tsx.cmd missing under "%ORCH_ROOT%\\node_modules\\.bin"
    exit /b 2
  )
)
set "EXIT_CODE=%ERRORLEVEL%"
popd >nul

python "%REPO_ROOT%\scripts\log_event.py" --event-type "run_phase.end" --summary "End phase plan %PLAN_PATH% exit_code=%EXIT_CODE%" --actor "wrapper" --ref "kind=cmd,path=run_phase.cmd" >nul 2>nul

python "%REPO_ROOT%\scripts\write_last_run_report.py" --repo-root "%REPO_ROOT%" --kind phase --exit-code %EXIT_CODE% --plan-path "%PLAN_PATH%" --baseline-branch "%BASELINE_BRANCH%" >nul 2>nul

python "%REPO_ROOT%\scripts\post_relay_continue.py" --repo-root "%REPO_ROOT%" --phase-plan "%PLAN_PATH%" --orchestrator-exit-code %EXIT_CODE%
if errorlevel 1 exit /b 1
powershell -NoProfile -ExecutionPolicy Bypass -File "%REPO_ROOT%\scripts\notify_run_finished.ps1" -RepoRoot "%REPO_ROOT%" >nul 2>nul

python -c "import pathlib; pathlib.Path(r'%ACTIVE_RUN%').unlink(missing_ok=True)" >nul 2>nul

exit /b %EXIT_CODE%

:local_phase
set "PYTHONPATH=%REPO_ROOT%"
python "%REPO_ROOT%\scripts\ppe_relay_phase.py" --repo-root "%REPO_ROOT%" --plan "%PLAN_PATH%"
set "EXIT_CODE=%ERRORLEVEL%"
python "%REPO_ROOT%\scripts\log_event.py" --event-type "run_phase.end" --summary "End phase plan %PLAN_PATH% exit_code=%EXIT_CODE% (local)" --actor "wrapper" --ref "kind=cmd,path=run_phase.cmd" >nul 2>nul
python "%REPO_ROOT%\scripts\write_last_run_report.py" --repo-root "%REPO_ROOT%" --kind phase --exit-code %EXIT_CODE% --plan-path "%PLAN_PATH%" --baseline-branch "%BASELINE_BRANCH%" >nul 2>nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%REPO_ROOT%\scripts\notify_run_finished.ps1" -RepoRoot "%REPO_ROOT%" >nul 2>nul
python -c "import pathlib; pathlib.Path(r'%ACTIVE_RUN%').unlink(missing_ok=True)" >nul 2>nul
exit /b %EXIT_CODE%

