@echo off
REM === DESKTOP ONLY — stop background auto-operator ===

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\ppe_desktop_auto_operator.py" --repo-root "%CD%" --stop
echo.
pause
