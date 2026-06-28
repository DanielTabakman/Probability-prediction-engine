@echo off
setlocal
REM Daily cross-venue probability panel snapshot (Deribit + Polymarket BTC).
REM See docs/SOP/CROSS_VENUE_COLLECTOR_OPS_V1.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\collect_cross_venue_snapshot.py" %*
set "RC=%ERRORLEVEL%"
if errorlevel 1 (
  echo collect_cross_venue_snapshot: FAILED exit=%RC%
) else (
  echo collect_cross_venue_snapshot: OK
)
exit /b %RC%
