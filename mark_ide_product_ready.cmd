@echo off
setlocal

REM Mark IDE product BUILD complete (after commit on build branch).
REM Usage: mark_ide_product_ready.cmd <sliceId> [phasePlanPath]

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

if "%~1"=="" (
  echo usage: mark_ide_product_ready.cmd ^<sliceId^> [phasePlanPath]
  exit /b 2
)

if "%~2"=="" (
  python "%CD%\scripts\ppe_ide_product_ready.py" --repo-root "%CD%" --mark --slice-id "%~1"
) else (
  python "%CD%\scripts\ppe_ide_product_ready.py" --repo-root "%CD%" --mark --slice-id "%~1" --plan "%~2"
)
exit /b %ERRORLEVEL%
