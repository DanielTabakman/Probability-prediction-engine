@echo off
setlocal

REM Task Scheduler logon entry: start operator stack; ntfy phone if startup fails.
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_local.cmd" call "%CD%\ppe_operator_local.cmd"

if exist "%CD%\run_ppe_desktop_operator.cmd" (
  call "%CD%\run_ppe_desktop_operator.cmd"
) else (
  call "%CD%\start_ppe_desktop_operator.cmd"
)
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
  if exist "%CD%\scripts\ppe_notify_push.py" (
    python "%CD%\scripts\ppe_notify_push.py" --title "PPE logon failed" --body "Desktop operator did not start after reboot. Exit code %RC%. Open the PC and run run_ppe_desktop_operator.cmd."
  )
)
exit /b %RC%
