@echo off
setlocal
REM Daily Options Horizon surface snapshot (Deribit BTC). VM Task Scheduler or manual.
REM See docs/SOP/HORIZON_SURFACE_COLLECTOR_OPS_V1.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\collect_horizon_surface_snapshot.py" %*
set "RC=%ERRORLEVEL%"
if errorlevel 1 (
  echo collect_horizon_surface_snapshot: FAILED exit=%RC%
) else (
  echo collect_horizon_surface_snapshot: OK
)
exit /b %RC%
