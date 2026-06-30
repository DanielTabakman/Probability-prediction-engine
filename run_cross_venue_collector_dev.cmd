@echo off
setlocal
REM Dev: high-cadence cross-venue snapshots for pipeline smoke (not production).
REM Usage: run_cross_venue_collector_dev.cmd --interval 300 --count 12

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\run_cross_venue_collector_dev.py" %*
set "RC=%ERRORLEVEL%"
if errorlevel 1 (
  echo run_cross_venue_collector_dev: FAILED exit=%RC%
) else (
  echo run_cross_venue_collector_dev: OK
)
exit /b %RC%
