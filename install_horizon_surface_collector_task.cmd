@echo off
setlocal
REM One-time: register daily horizon surface collector (run on VM loop host).
REM Usage: install_horizon_surface_collector_task.cmd
REM        install_horizon_surface_collector_task.cmd --unregister

cd /d "%~dp0"
python scripts/ppe_loop_host_guard.py --check >nul 2>&1
if errorlevel 1 (
  echo WARNING: ppe_loop_host_guard reports this machine is not the loop host.
  echo Install on the Hyper-V VM ^(ppeloop^) for 24/7 archive collection.
  echo Continuing anyway...
  echo.
)

set "PS_ARGS=-RepoRoot ""%CD%"""
if /i "%~1"=="--unregister" set "PS_ARGS=%PS_ARGS% -Unregister"

powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\scripts\install_ppe_horizon_surface_collector_task.ps1" %PS_ARGS%
exit /b %ERRORLEVEL%
