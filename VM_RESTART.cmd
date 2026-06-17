@echo off
REM === VM ONLY — safe full restart: STOP + wait + START (one double-click) ===
REM Same as running VM_STOP then VM_START, but in the right order automatically.

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

echo [VM_RESTART] step 1/5 — git pull...
git pull origin main
if errorlevel 1 (
  echo [VM_RESTART] git pull failed — fix network or conflicts, then try again.
  goto done
)

echo.
echo [VM_RESTART] step 2/5 — stop all workers (prevents popup storm)...
call "%~dp0fix_vm_stop_all.cmd" --no-pause

echo.
echo [VM_RESTART] step 3/5 — waiting 30 seconds for processes to exit...
echo            Close any blank cmd windows by hand if you still see them.
timeout /t 30 /nobreak

echo.
echo [VM_RESTART] step 4/5 — ensure loop-host env + start headless stack...
if not exist "%CD%\ppe_operator_loop_host.local.cmd" (
  if exist "%CD%\ppe_operator_loop_host.local.cmd.example" (
    copy /Y "%CD%\ppe_operator_loop_host.local.cmd.example" "%CD%\ppe_operator_loop_host.local.cmd" >nul
    echo [VM_RESTART] created ppe_operator_loop_host.local.cmd
  )
)
set "PPE_OPERATOR_PROFILE=local"
set "PPE_SKIP_ACP=1"
set "PPE_STACK_HEADLESS=1"
call "%CD%\run_ppe_headless_stack.cmd" --ensure
if errorlevel 1 (
  echo [VM_RESTART] headless start failed — see artifacts\orchestrator\HEADLESS_STACK_SUPERVISOR.log
  goto done
)

echo.
echo [VM_RESTART] step 5/5 — status:
call "%CD%\check_vm_loop.cmd" --no-pause

:done
echo.
echo ============================================================
echo  RESTART complete. If blank cmd windows keep appearing, run VM_STOP
echo  and do NOT click VM_RESTART again until they are gone.
echo ============================================================
echo.
pause
