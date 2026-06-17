@echo off
REM === DESKTOP ONLY — after BUILD is merged: mark ready + continue relay on VM ===
REM Double-click when Cursor BUILD is done (or PR merged to main).

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_no_loop.local.cmd" call "%CD%\ppe_operator_no_loop.local.cmd"
set "PPE_OPERATOR_PROFILE=local"

python "%CD%\scripts\ppe_operator_shortcuts.py" --repo-root "%CD%" --apply --quiet 2>nul

echo [DESKTOP_CONTINUE] step 1/3 — git pull...
git pull origin main
if errorlevel 1 (
  echo git pull failed.
  goto done
)

echo.
echo [DESKTOP_CONTINUE] step 2/3 — mark product ready + start relay on VM...
echo            (via SSH to ppeloop@desktop-caqll8k)
echo.

ssh ppeloop@desktop-caqll8k "cd /d C:\Users\ppeloop\Probability-prediction-engine && git pull origin main && finish_ide_build.cmd"
set "RC=%ERRORLEVEL%"

echo.
echo [DESKTOP_CONTINUE] step 3/3 — VM status:
ssh ppeloop@desktop-caqll8k "cd /d C:\Users\ppeloop\Probability-prediction-engine && ppe_autobuilder.cmd status --brief"
set "RC=%ERRORLEVEL%"

:done
echo.
echo ============================================================
echo  Done. VM loop should advance past IDE_BUILD.
echo ============================================================
echo.
echo Press any key to close...
pause >nul
exit /b %RC%
