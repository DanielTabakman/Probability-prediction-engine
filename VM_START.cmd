@echo off
REM === VM ONLY — double-click ONCE after VM_STOP (not repeatedly) ===
REM Pulls latest code, stops old workers, starts headless loop once.

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

echo [VM_START] step 1/4 — git pull...
git pull origin main
if errorlevel 1 (
  echo [VM_START] git pull failed — fix network or conflicts, then try again.
  goto done
)

echo.
echo [VM_START] step 2/4 — stop old workers (prevents popup storm)...
call "%~dp0fix_vm_stop_all.cmd" --no-pause
timeout /t 5 /nobreak >nul

echo.
echo [VM_START] step 3/4 — ensure loop-host env file...
if not exist "%CD%\ppe_operator_loop_host.local.cmd" (
  if exist "%CD%\ppe_operator_loop_host.local.cmd.example" (
    copy /Y "%CD%\ppe_operator_loop_host.local.cmd.example" "%CD%\ppe_operator_loop_host.local.cmd" >nul
    echo [VM_START] created ppe_operator_loop_host.local.cmd
  )
)

echo.
echo [VM_START] step 4/4 — start headless stack (one supervisor, no popup windows)...
set "PPE_OPERATOR_PROFILE=local"
set "PPE_SKIP_ACP=1"
set "PPE_STACK_HEADLESS=1"
call "%CD%\run_ppe_headless_stack.cmd" --ensure
if errorlevel 1 (
  echo [VM_START] headless start failed — see artifacts\orchestrator\HEADLESS_STACK_SUPERVISOR.log
  goto done
)

echo.
echo [VM_START] status:
call "%CD%\ppe_autobuilder.cmd" status --brief

:done
echo.
echo ============================================================
echo  If you see new blank cmd windows in the next minute, run VM_STOP
echo  and tell the desktop agent — do NOT click VM_START again.
echo ============================================================
echo.
pause
