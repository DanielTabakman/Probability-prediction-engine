@echo off
setlocal
REM Stop desktop zero-click IDE BUILD daemons.

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\ppe_desktop_zero_click_build.py" --repo-root "%CD%" --stop
exit /b %ERRORLEVEL%
