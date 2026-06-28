@echo off
setlocal
REM One-shot: desktop IDE-only + VM loop-host bootstrap (no manual SSH).
REM Run from daily PC repo root. Requires: ssh ppeloop@desktop-caqll8k

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
set "VM_HOST=ppeloop@desktop-caqll8k"
set "VM_REPO=C:\Users\ppeloop\Probability-prediction-engine"

echo [bootstrap_operator_pair] desktop IDE-only...
call "%CD%\setup_desktop_ide_only.cmd"

echo.
echo [bootstrap_operator_pair] VM git pull + loop-host config...
ssh -o BatchMode=yes -o ConnectTimeout=20 %VM_HOST% "cd /d %VM_REPO% && git pull origin main && if not exist ppe_operator_loop_host.local.cmd call setup_vm_loop_host.cmd"
if errorlevel 1 (
  echo [bootstrap_operator_pair] VM SSH failed — check ssh %VM_HOST%
  goto done
)

echo.
echo [bootstrap_operator_pair] VM logon task + watchdog + horizon collector + headless stack...
ssh -o BatchMode=yes %VM_HOST% "powershell -NoProfile -ExecutionPolicy Bypass -File %VM_REPO%\scripts\install_ppe_vm_headless_logon_task.ps1 -RepoRoot %VM_REPO%"
ssh -o BatchMode=yes %VM_HOST% "powershell -NoProfile -ExecutionPolicy Bypass -File %VM_REPO%\scripts\install_ppe_vm_watchdog_task.ps1 -RepoRoot %VM_REPO%" 2>nul
ssh -o BatchMode=yes %VM_HOST% "powershell -NoProfile -ExecutionPolicy Bypass -File %VM_REPO%\scripts\install_ppe_horizon_surface_collector_task.ps1 -RepoRoot %VM_REPO%"
ssh -o BatchMode=yes %VM_HOST% "cd /d %VM_REPO% && run_ppe_headless_stack.cmd --ensure"

echo.
echo [bootstrap_operator_pair] VM status...
ssh -o BatchMode=yes %VM_HOST% "cd /d %VM_REPO% && set PYTHONPATH=%VM_REPO% && python scripts\ppe_autobuilder.py status --brief"

:done
echo.
echo [bootstrap_operator_pair] done.
pause
exit /b 0
