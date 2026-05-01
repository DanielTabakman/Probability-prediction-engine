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
if "%SPRINT_SPEC%"=="" set "SPRINT_SPEC=docs/SOP/SPRINT_004_PHASE_2.md"

set "DECLARED_PLANE=%~3"
if "%DECLARED_PLANE%"=="" set "DECLARED_PLANE=PRODUCT-PLANE"

set "BASELINE_BRANCH=recovery/frontier-steward-v2_1-baseline"

for /f "tokens=1-4 delims=/.- " %%a in ("%date%") do set "YYYYMMDD=%%d%%b%%c"
for /f "tokens=1-3 delims=:." %%a in ("%time%") do set "HHMMSS=%%a%%b%%c"
set "HHMMSS=%HHMMSS: =0%"

set "BUILD_BRANCH=build/auto/%SLICE_ID%-%YYYYMMDD%_%HHMMSS%"

REM Local-first logbook (append-only; gitignored).
python "%REPO_ROOT%\scripts\log_event.py" --event-type "run_slice.start" --summary "Start slice %SLICE_ID% (plane=%DECLARED_PLANE%, spec=%SPRINT_SPEC%)" --actor "wrapper" --ref "kind=cmd,path=run_slice.cmd" --ref "kind=doc,path=docs/SOP/MVP1_FRONTIER.md" >nul 2>nul

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
call npm run dev -- run-slice "%REPO_ROOT%" "%SLICE_ID%" "%SPRINT_SPEC%" "%BASELINE_BRANCH%" "%BUILD_BRANCH%" 15 30 2
set "EXIT_CODE=%ERRORLEVEL%"
popd >nul

python "%REPO_ROOT%\scripts\log_event.py" --event-type "run_slice.end" --summary "End slice %SLICE_ID% exit_code=%EXIT_CODE%" --actor "wrapper" --ref "kind=cmd,path=run_slice.cmd" >nul 2>nul

exit /b %EXIT_CODE%

