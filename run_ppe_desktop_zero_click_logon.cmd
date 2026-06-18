@echo off
setlocal
REM Task Scheduler logon entry: zero-click BUILD only (no relay loop on daily PC).

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_no_loop.local.cmd" call "%CD%\ppe_operator_no_loop.local.cmd"
set "PPE_OPERATOR_PROFILE=local"
set "PPE_DESKTOP_AUTO=1"

python "%CD%\scripts\ppe_operator_git_sync.py" --repo-root "%CD%" --pull
python "%CD%\scripts\ppe_desktop_zero_click_build.py" --repo-root "%CD%" --start
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
  if exist "%CD%\scripts\ppe_notify_push.py" (
    python "%CD%\scripts\ppe_notify_push.py" --title "PPE zero-click start failed" --body "Desktop zero-click BUILD did not start after logon. Exit %RC%. Run DESKTOP ZERO CLICK START."
  )
)
exit /b %RC%
