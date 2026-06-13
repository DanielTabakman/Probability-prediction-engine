@echo off
setlocal enabledelayedexpansion

REM Full IDE product slice closeout: gate, mark ready, run_ppe_local (git-sync safe on build branches).
REM Usage: ppe_ide_build_closeout.cmd <sliceId> <phasePlanPath>

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

if "%~1"=="" (
  echo usage: ppe_ide_build_closeout.cmd ^<sliceId^> ^<phasePlanPath^>
  exit /b 2
)
if "%~2"=="" (
  echo usage: ppe_ide_build_closeout.cmd ^<sliceId^> ^<phasePlanPath^>
  exit /b 2
)

set "SLICE_ID=%~1"
set "PLAN_PATH=%~2"

for /f "delims=" %%b in ('git branch --show-current 2^>nul') do set "CUR_BRANCH=%%b"
echo ppe_ide_build_closeout: branch=!CUR_BRANCH! slice=!SLICE_ID!

echo [1/3] pushable gate...
python "%CD%\scripts\run_pushable_gate.py"
if errorlevel 1 (
  echo ppe_ide_build_closeout: gate failed — fix before mark_ready
  exit /b 1
)

git diff --quiet && git diff --cached --quiet
if errorlevel 1 (
  echo ppe_ide_build_closeout: uncommitted changes remain — commit on build branch before mark_ready
  exit /b 1
)

echo [2/3] mark IDE product ready...
call "%CD%\mark_ide_product_ready.cmd" "!SLICE_ID!" "!PLAN_PATH!"
if errorlevel 1 exit /b 1

echo [3/3] run_ppe_local (git sync disabled on build/auto branches)...
if /i "!CUR_BRANCH:~0,11!"=="build/auto/" (
  set "PPE_GIT_SYNC_PULL=0"
  set "PPE_GIT_SYNC_PUSH=0"
)
call "%CD%\run_ppe_local.cmd"
exit /b %ERRORLEVEL%
