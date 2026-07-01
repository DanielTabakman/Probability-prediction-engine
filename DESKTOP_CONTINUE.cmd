@echo off
setlocal

REM === DESKTOP ONLY — after BUILD is merged: mark ready + continue relay on VM ===
REM Double-click when Cursor BUILD is done (or PR merged to main).
REM Agent/non-interactive: DESKTOP_CONTINUE.cmd --no-pause

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_no_loop.local.cmd" call "%CD%\ppe_operator_no_loop.local.cmd"
set "PPE_OPERATOR_PROFILE=local"
set "NO_PAUSE=0"
if /i "%~1"=="--no-pause" set "NO_PAUSE=1"

python "%CD%\scripts\ppe_operator_shortcuts.py" --repo-root "%CD%" --apply --quiet 2>nul
python "%CD%\scripts\ppe_desktop_continue.py" --repo-root "%CD%"
set "RC=%ERRORLEVEL%"

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
