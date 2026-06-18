@echo off
setlocal
REM One-time desktop zero-click IDE BUILD setup (VM loop + desktop agent CLI).
REM See docs/SOP/CURSOR_IDE_BUILD_AUTOMATION_V1.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_no_loop.local.cmd" call "%CD%\ppe_operator_no_loop.local.cmd"
set "PPE_OPERATOR_PROFILE=local"

echo ============================================================
echo  PPE desktop zero-click BUILD setup
echo ============================================================
echo.

echo [1/3] Cursor Agent CLI...
call "%CD%\setup_cursor_agent.cmd"
echo.

echo [2/3] Prerequisites (no-loop guard, opt-in token, shortcuts)...
python "%CD%\scripts\ppe_desktop_zero_click_build.py" --repo-root "%CD%" --setup --install-logon
if errorlevel 1 (
  echo.
  echo Setup incomplete — fix agent login if needed: agent login
  goto done
)

echo.
echo [3/3] Starting zero-click daemons...
python "%CD%\scripts\ppe_desktop_zero_click_build.py" --repo-root "%CD%" --start
set "RC=%ERRORLEVEL%"

echo.
echo ============================================================
echo  Zero-click BUILD is active on this desktop.
echo.
echo  When the VM loop hits IDE_BUILD:
echo    - Auto-operator writes the handoff locally (~2 min)
echo    - Watcher dispatches agent CLI (~5 sec)
echo    - You only touch DESKTOP CONTINUE after PR merges
echo.
echo  Buttons: DESKTOP ZERO CLICK START / STOP
echo  Logon: Task Scheduler starts zero-click at login
echo ============================================================

:done
echo.
pause
exit /b %RC%
