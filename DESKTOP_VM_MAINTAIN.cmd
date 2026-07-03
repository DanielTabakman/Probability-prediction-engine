@echo off
REM === DESKTOP ONLY — VM update + stack restart via SSH ===
REM One double-click from daily PC. No Hyper-V console required.

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_no_loop.local.cmd" call "%CD%\ppe_operator_no_loop.local.cmd"
set "PPE_OPERATOR_PROFILE=local"
set "VM_HOST=ppeloop@desktop-caqll8k"
set "VM_REPO=C:\Users\ppeloop\Probability-prediction-engine"

python "%CD%\scripts\ppe_operator_shortcuts.py" --repo-root "%CD%" --apply --quiet 2>nul

echo [DESKTOP_VM_MAINTAIN] step 1/4 — desktop git pull...
git pull origin main
if errorlevel 1 (
  echo git pull failed on desktop.
  goto done
)

echo.
echo [DESKTOP_VM_MAINTAIN] step 2/4 — VM git pull + notify config...
ssh -o BatchMode=yes -o ConnectTimeout=30 %VM_HOST% "cd /d %VM_REPO% && git pull origin main && set PYTHONPATH=%VM_REPO% && python scripts\bootstrap_operator_notify_secret.py --repo-root ."
if errorlevel 1 (
  echo VM SSH step 2 failed.
  goto done
)

echo.
echo [DESKTOP_VM_MAINTAIN] step 3/4 — VM stack restart (headless)...
ssh -o BatchMode=yes %VM_HOST% "cd /d %VM_REPO% && call fix_vm_stop_all.cmd --no-pause && timeout /t 15 /nobreak >nul && set PPE_OPERATOR_PROFILE=local && set PPE_SKIP_ACP=1 && set PPE_STACK_HEADLESS=1 && call run_ppe_headless_stack.cmd --ensure"
if errorlevel 1 (
  echo VM stack ensure failed — check VM HEADLESS_STACK_SUPERVISOR.log
  goto done
)

echo.
echo [DESKTOP_VM_MAINTAIN] step 4/4 — VM status:
ssh -o BatchMode=yes %VM_HOST% "cd /d %VM_REPO% && set PYTHONPATH=%VM_REPO% && python scripts\ppe_autobuilder.py status --brief"

:done
echo.
echo ============================================================
echo  VM maintain complete. Loop runs on VM only; desktop stays IDE-only.
echo ============================================================
echo.
pause
exit /b 0
