@echo off
setlocal enabledelayedexpansion

REM Thin wrapper: run one slice through relay-gated ACP orchestrator.
REM Usage:
REM   run_slice.cmd <sliceId> [sprintSpecPath] [declaredPlane]

set "REPO_ROOT=%~dp0"
set "REPO_ROOT=%REPO_ROOT:~0,-1%"

set "SLICE_ID=%~1"
if "%SLICE_ID%"=="" (
  echo usage: run_slice.cmd ^<sliceId^> [sprintSpecPath] [declaredPlane]
  exit /b 2
)

set "SPRINT_SPEC=%~2"
if "%SPRINT_SPEC%"=="" set "SPRINT_SPEC=docs/SOP/SPRINT_VALIDATION_CHAPTER.md"

set "DECLARED_PLANE=%~3"
if "%DECLARED_PLANE%"=="" set "DECLARED_PLANE=PRODUCT-PLANE"

set "BASELINE_BRANCH=main"

for /f "tokens=1-4 delims=/.- " %%a in ("%date%") do set "YYYYMMDD=%%d%%b%%c"
for /f "tokens=1-3 delims=:." %%a in ("%time%") do set "HHMMSS=%%a%%b%%c"
set "HHMMSS=%HHMMSS: =0%"

set "BUILD_BRANCH=build/auto/%SLICE_ID%-%YYYYMMDD%_%HHMMSS%"

set "ACTIVE_RUN=%REPO_ROOT%\\artifacts\\orchestrator\\ACTIVE_RUN.json"
if not exist "%REPO_ROOT%\\artifacts\\orchestrator" (
  mkdir "%REPO_ROOT%\\artifacts\\orchestrator" >nul 2>nul
)

REM Local-first logbook (append-only; gitignored).
python "%REPO_ROOT%\scripts\log_event.py" --event-type "run_slice.start" --summary "Start slice %SLICE_ID% (plane=%DECLARED_PLANE%, spec=%SPRINT_SPEC%)" --actor "wrapper" --ref "kind=cmd,path=run_slice.cmd" --ref "kind=doc,path=docs/SOP/MVP1_FRONTIER.md" >nul 2>nul

REM Write an explicit active-run marker so the steward can tell if anything is in-flight.
python -c "import json,datetime,pathlib; p=r'%ACTIVE_RUN%'; d={'kind':'slice','slice_id':r'%SLICE_ID%','declared_plane':r'%DECLARED_PLANE%','sprint_spec':r'%SPRINT_SPEC%','baseline_branch':r'%BASELINE_BRANCH%','build_branch':r'%BUILD_BRANCH%','ts_utc':datetime.datetime.utcnow().replace(microsecond=0).isoformat()+'Z'}; pathlib.Path(p).parent.mkdir(parents=True, exist_ok=True); pathlib.Path(p).write_text(json.dumps(d,indent=2), encoding='utf-8')" >nul 2>nul

set "ORCH_ROOT=%USERPROFILE%\Desktop\ppe-orchestrator-acp"
if not exist "%ORCH_ROOT%\package.json" (
  set "ORCH_ROOT=%REPO_ROOT%\..\ppe-orchestrator-acp"
)

REM Prefer portable Node 20 used elsewhere if present.
set "NODE20=%USERPROFILE%\Desktop\ppe-orchestrator-sdk\node\node-v20.18.2-win-x64"
if exist "%NODE20%\npm.cmd" (
  set "PATH=%NODE20%;%PATH%"
)

pushd "%ORCH_ROOT%" >nul
REM ACP permissions are handled programmatically by the orchestrator; this avoids relying on Cursor popups.
REM Modes: allow-once (default) or allow-always (reduces repeated permission prompts).
set "ACP_PERMISSION_MODE=allow-always"
REM Prefer npm if available; otherwise run tsx directly (node_modules is already present).
where npm >nul 2>nul
if "%ERRORLEVEL%"=="0" (
  call npm run dev -- run-slice "%REPO_ROOT%" "%SLICE_ID%" "%SPRINT_SPEC%" "%BASELINE_BRANCH%" "%BUILD_BRANCH%" 15 30 2
) else (
  if exist "%ORCH_ROOT%\\node_modules\\.bin\\tsx.cmd" (
    call "%ORCH_ROOT%\\node_modules\\.bin\\tsx.cmd" src\\cli.ts run-slice "%REPO_ROOT%" "%SLICE_ID%" "%SPRINT_SPEC%" "%BASELINE_BRANCH%" "%BUILD_BRANCH%" 15 30 2
  ) else (
    echo ERROR: npm not found and tsx.cmd missing under "%ORCH_ROOT%\\node_modules\\.bin"
    exit /b 2
  )
)
set "EXIT_CODE=%ERRORLEVEL%"
popd >nul

python "%REPO_ROOT%\scripts\log_event.py" --event-type "run_slice.end" --summary "End slice %SLICE_ID% exit_code=%EXIT_CODE%" --actor "wrapper" --ref "kind=cmd,path=run_slice.cmd" >nul 2>nul

python "%REPO_ROOT%\scripts\write_last_run_report.py" --repo-root "%REPO_ROOT%" --kind slice --exit-code %EXIT_CODE% --slice-id "%SLICE_ID%" --baseline-branch "%BASELINE_BRANCH%" --build-branch "%BUILD_BRANCH%" --sprint-spec "%SPRINT_SPEC%" --declared-plane "%DECLARED_PLANE%" >nul 2>nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%REPO_ROOT%\scripts\notify_run_finished.ps1" -RepoRoot "%REPO_ROOT%" >nul 2>nul

REM Clear active-run marker on completion.
python -c "import pathlib; pathlib.Path(r'%ACTIVE_RUN%').unlink(missing_ok=True)" >nul 2>nul

exit /b %EXIT_CODE%

