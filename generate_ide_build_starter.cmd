@echo off
setlocal

REM Generate IDE BUILD starter (one-file LOAD-ALWAYS bundle).
REM Usage: generate_ide_build_starter.cmd <sliceId> <phasePlanPath>

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

if "%~2"=="" (
  echo usage: generate_ide_build_starter.cmd ^<sliceId^> ^<phasePlanPath^>
  exit /b 2
)

python "%CD%\scripts\ppe_ide_build_starter.py" --repo-root "%CD%" --slice-id "%~1" --phase-plan "%~2"
exit /b %ERRORLEVEL%
