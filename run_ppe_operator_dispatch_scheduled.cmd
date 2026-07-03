@echo off
setlocal
REM Scheduled operator dispatch — requires ppe_operator_desktop_auto.local.cmd (opt-in).
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_no_loop.local.cmd" call "%CD%\ppe_operator_no_loop.local.cmd"
if not exist "%CD%\ppe_operator_desktop_auto.local.cmd" (
  echo ppe_operator_dispatch_scheduled: skipped — missing opt-in token
  exit /b 0
)
set "PPE_AUTO_DISPATCH=1"
python "%CD%\scripts\ppe_operator_dispatch.py" --repo-root "%CD%" --from-status --auto --json >> "%CD%\artifacts\orchestrator\OPERATOR_DISPATCH_SCHEDULED.log" 2>&1
exit /b 0
