@echo off
setlocal
REM Score cross-venue gap history when >=14 daily snapshots exist.
REM See docs/SOP/CROSS_VENUE_COLLECTOR_OPS_V1.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\run_cross_venue_backtest.py" %*
set "RC=%ERRORLEVEL%"
if errorlevel 1 (
  echo run_cross_venue_backtest: FAILED exit=%RC%
) else (
  echo run_cross_venue_backtest: OK
)
exit /b %RC%
