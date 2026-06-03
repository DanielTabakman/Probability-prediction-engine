@echo off
setlocal

REM Generate slim BUILD packet for a slice.
REM Usage: generate_build_packet.cmd <sliceId> <phasePlanPath>
REM    or: generate_build_packet.cmd --manifest

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

if "%~1"=="--manifest" (
  python "%CD%\scripts\ppe_build_packet.py" --repo-root "%CD%" --manifest --score
  exit /b %ERRORLEVEL%
)

if "%~2"=="" (
  echo usage: generate_build_packet.cmd ^<sliceId^> ^<phasePlanPath^>
  echo    or: generate_build_packet.cmd --manifest
  exit /b 2
)

python "%CD%\scripts\ppe_build_packet.py" --repo-root "%CD%" --slice-id "%~1" --phase-plan "%~2" --score
exit /b %ERRORLEVEL%
