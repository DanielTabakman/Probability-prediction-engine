@echo off
setlocal
REM VM one-shot: loop-host token, logon stack, watchdog, horizon collector, ensure stack running.
REM Run once on the Hyper-V loop host (ppeloop). Idempotent — safe to re-run.
REM See docs/SOP/PPE_VM_LOOP_HOST_V1.md · docs/SOP/HORIZON_SURFACE_COLLECTOR_OPS_V1.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
set "RC=0"

echo [setup_vm_hands_off] step 1/6 — loop-host env token...
if exist "%CD%\setup_vm_loop_host.cmd" (
  call "%CD%\setup_vm_loop_host.cmd"
) else (
  echo [setup_vm_hands_off] missing setup_vm_loop_host.cmd
  set "RC=1"
  goto done
)

call "%CD%\call_ppe_operator_local.cmd"
python "%CD%\scripts\ppe_loop_host_guard.py" --check
if errorlevel 1 (
  echo [setup_vm_hands_off] loop-host guard failed — fix ppe_operator_loop_host.local.cmd
  set "RC=1"
  goto done
)

echo.
echo [setup_vm_hands_off] step 2/6 — headless stack logon task...
powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\scripts\install_ppe_vm_headless_logon_task.ps1" -RepoRoot "%CD%"
if errorlevel 1 set "RC=1"

echo.
echo [setup_vm_hands_off] step 3/6 — VM watchdog task...
powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\scripts\install_ppe_vm_watchdog_task.ps1" -RepoRoot "%CD%"
if errorlevel 1 set "RC=1"

echo.
echo [setup_vm_hands_off] step 4/6 — horizon surface collector (daily 06:30)...
call "%CD%\install_horizon_surface_collector_task.cmd"
if errorlevel 1 set "RC=1"

echo.
echo [setup_vm_hands_off] step 5/6 — ensure headless stack now...
call "%CD%\run_ppe_headless_stack.cmd" --ensure
if errorlevel 1 set "RC=1"

echo.
echo [setup_vm_hands_off] step 6/6 — seed horizon archive (manual snapshot)...
call "%CD%\collect_horizon_surface_snapshot.cmd"
if errorlevel 1 set "RC=1"

echo.
call "%CD%\check_vm_loop.cmd" --no-pause

:done
echo.
if "%RC%"=="0" (
  echo [setup_vm_hands_off] OK — VM should self-start after reboot. Use VM_STATUS.cmd to triage.
) else (
  echo [setup_vm_hands_off] finished with errors ^(exit=%RC%^)
)
exit /b %RC%
