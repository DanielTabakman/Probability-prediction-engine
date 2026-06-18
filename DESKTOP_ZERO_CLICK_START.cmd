@echo off
setlocal
REM Start desktop zero-click IDE BUILD (watcher + auto handoff). No relay loop.

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_no_loop.local.cmd" call "%CD%\ppe_operator_no_loop.local.cmd"
set "PPE_OPERATOR_PROFILE=local"
set "PPE_DESKTOP_AUTO=1"

python "%CD%\scripts\ppe_operator_shortcuts.py" --repo-root "%CD%" --apply --quiet 2>nul
python "%CD%\scripts\ppe_desktop_zero_click_build.py" --repo-root "%CD%" --start
exit /b %ERRORLEVEL%
