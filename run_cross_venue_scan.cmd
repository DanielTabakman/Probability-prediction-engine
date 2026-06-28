@echo off
setlocal
REM Rank cross-venue gaps from live fetch or latest snapshot.
REM See docs/SOP/CROSS_VENUE_COLLECTOR_OPS_V1.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\run_cross_venue_scan.py" %*
set "RC=%ERRORLEVEL%"
if errorlevel 1 (
  echo run_cross_venue_scan: FAILED exit=%RC%
) else (
  echo run_cross_venue_scan: OK
)
exit /b %RC%
