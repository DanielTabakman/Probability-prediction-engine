@echo off
setlocal

REM === DESKTOP ONLY — after BUILD is merged: mark ready + continue relay on VM ===
REM Double-click when Cursor BUILD is done (or PR merged to main).
REM Agent/non-interactive: DESKTOP_CONTINUE.cmd --no-pause

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_no_loop.local.cmd" call "%CD%\ppe_operator_no_loop.local.cmd"
set "PPE_OPERATOR_PROFILE=local"
set "PPE_OPERATOR_STATUS_PATCH_MAP=0"
set "SSH_OPTS=-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=10 -o ServerAliveCountMax=3"
if defined PPE_VM_SSH_HOST (set "VM_HOST=%PPE_VM_SSH_HOST%") else set "VM_HOST=ppe-vm"
set "VM_REPO=C:\Users\ppeloop\Probability-prediction-engine"
set "NO_PAUSE=0"
if /i "%~1"=="--no-pause" set "NO_PAUSE=1"

python "%CD%\scripts\ppe_operator_shortcuts.py" --repo-root "%CD%" --apply --quiet 2>nul

echo [DESKTOP_CONTINUE] step 0/4 — chapter coordination repair (desktop)...
python "%CD%\scripts\ppe_prepare_desktop_handoff.py" --repo-root "%CD%"
set "PREP_RC=%ERRORLEVEL%"
if not "%PREP_RC%"=="0" (
  echo.
  echo Coordination repair did not reach RUN_LOCAL — fix above, then retry.
  echo See docs/SOP/CHAPTER_COORDINATION_V1.md
  set "RC=%PREP_RC%"
  goto done
)

echo [DESKTOP_CONTINUE] step 1/4 — mirror sync (merge mirror PRs + pull main)...
python "%CD%\scripts\ppe_operator_vm_mirror_refresh.py" --sync-desktop --repo-root "%CD%"
if errorlevel 1 (
  echo mirror sync failed — fix git/gh auth or dirty tree, then retry.
  goto done
)

echo.
echo [DESKTOP_CONTINUE] step 2/4 — VM coordination repair + finish handoff...
echo            (via SSH to %VM_HOST%)
echo.

ssh %SSH_OPTS% %VM_HOST% "cd /d %VM_REPO% && call call_ppe_operator_local.cmd && set PYTHONPATH=%VM_REPO% && python scripts/ppe_chapter_coordination.py --repair && python scripts/ppe_operator_git_sync.py --repo-root %VM_REPO% --prepare-handoff-auto && finish_ide_build.cmd"
set "RC=%ERRORLEVEL%"

echo.
echo [DESKTOP_CONTINUE] step 3/4 — VM status:
ssh %SSH_OPTS% %VM_HOST% "cd /d %VM_REPO% && call call_ppe_operator_local.cmd && call check_vm_loop.cmd --no-pause"
set "RC=%ERRORLEVEL%"

echo.
echo [DESKTOP_CONTINUE] step 4/4 — closeout spine audit (desktop):
python "%CD%\scripts\ppe_chapter_coordination.py" --spine-audit --repo-root "%CD%"

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
