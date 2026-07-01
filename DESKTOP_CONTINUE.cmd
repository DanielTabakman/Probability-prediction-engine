@echo off
setlocal

REM === DESKTOP ONLY — after BUILD is merged: mark ready + continue relay on VM ===
REM Double-click when Cursor BUILD is done (or PR merged to main).
REM Agent/non-interactive: DESKTOP_CONTINUE.cmd --no-pause

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_no_loop.local.cmd" call "%CD%\ppe_operator_no_loop.local.cmd"
set "PPE_OPERATOR_PROFILE=local"
set "SSH_OPTS=-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=10 -o ServerAliveCountMax=3"
if defined PPE_VM_SSH_HOST (set "VM_HOST=%PPE_VM_SSH_HOST%") else set "VM_HOST=ppe-vm"
set "VM_REPO=C:\Users\ppeloop\Probability-prediction-engine"
set "NO_PAUSE=0"
if /i "%~1"=="--no-pause" set "NO_PAUSE=1"

python "%CD%\scripts\ppe_operator_shortcuts.py" --repo-root "%CD%" --apply --quiet 2>nul

echo [DESKTOP_CONTINUE] step 1/3 — git pull...
git pull origin main
if errorlevel 1 (
  echo git pull failed.
  goto done
)

echo.
echo [DESKTOP_CONTINUE] step 2/3 — mark product ready + start relay on VM...
echo            (via SSH to %VM_HOST%)
echo.

ssh %SSH_OPTS% %VM_HOST% "cd /d %VM_REPO% && git pull origin main && call call_ppe_operator_local.cmd && finish_ide_build.cmd"
set "RC=%ERRORLEVEL%"

echo.
echo [DESKTOP_CONTINUE] step 3/3 — VM status:
ssh %SSH_OPTS% %VM_HOST% "cd /d %VM_REPO% && call call_ppe_operator_local.cmd && ppe_autobuilder.cmd status --brief"
set "RC=%ERRORLEVEL%"

:done
echo.
echo ============================================================
echo  Done. VM loop should advance past IDE_BUILD.
echo ============================================================
echo.
if "%NO_PAUSE%"=="0" (
  echo Press any key to close...
  pause >nul
)
exit /b %RC%
