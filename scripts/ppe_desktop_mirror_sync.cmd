@echo off
setlocal
REM Desktop-only: merge VM mirror PRs + pull main + refresh local phase mirror.
cd /d "%~dp0\.."
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_no_loop.local.cmd" call "%CD%\ppe_operator_no_loop.local.cmd"
python "%CD%\scripts\ppe_operator_vm_mirror_refresh.py" --sync-desktop --repo-root "%CD%" --quiet 2>nul
if errorlevel 1 (
  python "%CD%\scripts\ppe_operator_vm_mirror_refresh.py" --sync-desktop --repo-root "%CD%"
)
exit /b %ERRORLEVEL%
