@echo off
REM === DESKTOP ONLY — unified BUILD handoff (Cursor or Codex) ===
REM Copies build prompt to clipboard via ppe_autobuilder handoff.

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
python "%CD%\scripts\ppe_build_worker.py" --repo-root "%CD%" print-handoff
echo.
echo ============================================================
echo.

:done
echo Press any key to close...
pause >nul
exit /b %RC%
