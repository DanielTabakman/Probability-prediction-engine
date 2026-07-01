@echo off
REM === DESKTOP ONLY — unified BUILD handoff (Cursor or Codex) ===
REM Stages starter + IDE_BUILD_NOW.md via ppe_autobuilder handoff (clipboard off by default).

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_no_loop.local.cmd" call "%CD%\ppe_operator_no_loop.local.cmd"
set "PPE_OPERATOR_PROFILE=local"

python "%CD%\scripts\ppe_operator_shortcuts.py" --repo-root "%CD%" --apply --quiet 2>nul

echo [DESKTOP_BUILD] Checking operator status...
echo.

python "%CD%\scripts\ppe_operator_env.py"
if errorlevel 1 goto done

echo [DESKTOP_BUILD] Worker lane + lease (ARCP)...
python "%CD%\scripts\ppe_worker_lease.py" --repo-root "%CD%" --prepare-desktop-build
if errorlevel 1 (
  echo.
  echo [DESKTOP_BUILD] BLOCKED — resolve lease conflict before BUILD.
  echo   python scripts/ppe_worker_lease.py --assess
  echo   docs/SOP/WORKER_LANE_POLICY_V1.md
  set "RC=1"
  goto done
)
echo.

python -u "%CD%\scripts\ppe_autobuilder.py" --repo-root "%CD%" handoff
set "RC=%ERRORLEVEL%"

echo.
python "%CD%\scripts\ppe_build_worker.py" --repo-root "%CD%" print-handoff
echo.
echo ============================================================
echo.

:done
echo Press any key to close...
pause >nul
exit /b %RC%
