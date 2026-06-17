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
echo  Cursor should open. If not, open it yourself.
echo  In a NEW Agent chat: press Ctrl+V then Enter.
echo  (Build prompt is on your clipboard.)
echo ============================================================
echo.

:done
echo Press any key to close...
pause >nul
exit /b %RC%
