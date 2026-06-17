@echo off
REM === DESKTOP ONLY — start auto-operator (pushes BUILD/CONTINUE for you) ===
REM Run once after login. Checks every ~2 minutes.

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_no_loop.local.cmd" call "%CD%\ppe_operator_no_loop.local.cmd"
set "PPE_OPERATOR_PROFILE=local"
set "PPE_DESKTOP_AUTO=1"

python "%CD%\scripts\ppe_operator_shortcuts.py" --repo-root "%CD%" --apply --quiet 2>nul

echo [DESKTOP_AUTO_START] starting background helper...
python "%CD%\scripts\ppe_desktop_auto_operator.py" --repo-root "%CD%" --start
if errorlevel 1 (
  echo [DESKTOP_AUTO_START] failed to start — see artifacts\orchestrator\DESKTOP_AUTO_OPERATOR.log
  goto done
)

echo.
echo ============================================================
echo  AUTO is ON. The PC will:
echo    - Open Cursor when IDE BUILD is needed
echo    - Continue the VM relay after merges
echo  You can still use DESKTOP BUILD / CONTINUE manually.
echo  To stop: DESKTOP AUTO STOP
echo ============================================================

:done
echo.
pause
