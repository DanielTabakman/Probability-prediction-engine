@echo off
REM === DO THE THING — one button for queued + smart operator actions ===
REM Queue: python scripts\ppe_do_the_thing.py add <action> --label "..."
REM Empty queue: runs status-derived plan (IDE BUILD, CONTINUE, VM advance, etc.)

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_local.cmd" call "%CD%\ppe_operator_local.cmd"
if exist "%CD%\ppe_operator_no_loop.local.cmd" call "%CD%\ppe_operator_no_loop.local.cmd"
set "PPE_OPERATOR_PROFILE=local"

python "%CD%\scripts\ppe_operator_shortcuts.py" --repo-root "%CD%" --apply --quiet 2>nul

echo.
echo ============================================================
echo   DO THE THING
echo ============================================================
echo.

python "%CD%\scripts\ppe_do_the_thing.py" --repo-root "%CD%" list
echo.

python "%CD%\scripts\ppe_do_the_thing.py" --repo-root "%CD%" run
set "RC=%ERRORLEVEL%"

echo.
echo ============================================================
if %RC%==0 (
  echo  Done.
) else (
  echo  Something failed — see artifacts\orchestrator\DO_THE_THING.log
)
echo ============================================================
echo.
echo Press any key to close...
pause >nul
exit /b %RC%
