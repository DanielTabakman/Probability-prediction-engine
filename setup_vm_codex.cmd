@echo off
setlocal
REM === DESKTOP ONLY — install + login Codex on VM loop host (option A) ===
REM One-time: enables headless auto BUILD on IDE_BUILD without DESKTOP_BUILD paste.

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_no_loop.local.cmd" call "%CD%\ppe_operator_no_loop.local.cmd"
set "PPE_OPERATOR_PROFILE=local"
set "VM_HOST=ppeloop@desktop-caqll8k"
set "VM_REPO=C:\Users\ppeloop\Probability-prediction-engine"

python "%CD%\scripts\ppe_operator_shortcuts.py" --repo-root "%CD%" --apply --quiet 2>nul

echo [setup_vm_codex] step 1/4 — VM git pull + Codex CLI install...
ssh -o BatchMode=yes -o ConnectTimeout=30 %VM_HOST% "cd /d %VM_REPO% && git pull origin main && setup_codex.cmd"
if errorlevel 1 (
  echo Install step failed or Codex not logged in yet — continuing to login.
)

echo.
echo [setup_vm_codex] step 2/4 — Codex login on VM (device code)
echo   WRONG: localhost:1455 URL  ^|  RIGHT: auth.openai.com/codex/device + code
echo.
ssh %VM_HOST% -- "cd /d %VM_REPO% && codex login --device-auth"
if errorlevel 1 (
  echo codex login failed or was cancelled.
  goto done
)

echo.
echo [setup_vm_codex] step 3/4 — verify BUILD worker on VM...
ssh -o BatchMode=yes %VM_HOST% "cd /d %VM_REPO% && set PYTHONPATH=%VM_REPO% && set PPE_OPERATOR_PROFILE=local && clear_build_worker_quota.cmd && verify_build_worker.cmd"
if errorlevel 1 (
  echo verify_build_worker failed on VM — check codex login status.
  goto done
)

echo.
echo [setup_vm_codex] step 4/4 — restart VM headless stack...
ssh -o BatchMode=yes %VM_HOST% "cd /d %VM_REPO% && call fix_vm_stop_all.cmd --no-pause && timeout /t 10 /nobreak >nul && set PPE_OPERATOR_PROFILE=local && set PPE_SKIP_ACP=1 && set PPE_STACK_HEADLESS=1 && call run_ppe_headless_stack.cmd --ensure"
if errorlevel 1 (
  echo VM stack restart failed — check HEADLESS_STACK_SUPERVISOR.log on VM.
  goto done
)

ssh -o BatchMode=yes %VM_HOST% "cd /d %VM_REPO% && set PYTHONPATH=%VM_REPO% && python scripts\ppe_autobuilder.py status --brief"

echo.
echo [setup_vm_codex] done — VM should auto-run headless Codex on IDE_BUILD.

:done
echo.
pause
exit /b 0
