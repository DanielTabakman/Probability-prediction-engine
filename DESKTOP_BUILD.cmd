@echo off
REM === DESKTOP ONLY — double-click to start IDE BUILD in Cursor ===
REM Opens the starter file and copies the build prompt to clipboard.

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_no_loop.local.cmd" call "%CD%\ppe_operator_no_loop.local.cmd"
set "PPE_OPERATOR_PROFILE=local"

python "%CD%\scripts\ppe_operator_shortcuts.py" --repo-root "%CD%" --apply --quiet 2>nul

echo [DESKTOP_BUILD] Checking operator status...
echo.

python "%CD%\scripts\ppe_operator_env.py"
if errorlevel 1 goto done

python -u "%CD%\scripts\ppe_autobuilder.py" --repo-root "%CD%" handoff
set "RC=%ERRORLEVEL%"

echo.
echo ============================================================
echo  DESKTOP BUILD — your real PC only (NOT the VM)
echo ============================================================
echo.
echo  The build prompt is already on your clipboard.
echo.
echo  1. Open Cursor on THIS machine (repo folder).
echo  2. Start a NEW Agent chat (not this chat).
echo  3. Press Ctrl+V, then Enter.
echo  4. Let the agent finish gate + commit + closeout.
echo  5. After PR merges: double-click DESKTOP CONTINUE.
echo.
echo  The VM loop keeps waiting — you do not run anything on the VM.
echo ============================================================
echo.

:done
echo Press any key to close...
pause >nul
exit /b %RC%
