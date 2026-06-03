@echo off
setlocal enabledelayedexpansion

REM Repeat run_ppe_auto until you stop it (Ctrl+C). Sleep between passes when idle.
REM idleSleepSeconds from docs/SOP/PPE_AUTO_OPERATOR.json (default 120).
REM Exit 7: guard stop (PRODUCT_BLOCKED, CONTEXT_ESCALATE, TOO_MANY_SLICES, etc.) — no sleep/retry.

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\ppe_workflow_loop_hooks.py" --repo-root "%CD%" --loop-start

set "SLEEP=120"
for /f "usebackq delims=" %%s in (`python -c "from pathlib import Path; from scripts.ppe_operator_config import idle_sleep_seconds; print(idle_sleep_seconds(Path('.')))"`) do set "SLEEP=%%s"

:loop
echo [run_ppe_auto_loop] starting pass at %DATE% %TIME%
call "%~dp0run_ppe_auto.cmd"
set "RC=%ERRORLEVEL%"
if "%RC%"=="7" (
  echo [run_ppe_auto_loop] operator guard stop — review artifacts/orchestrator/OPERATOR_GUARD_REPORT.md
  exit /b 7
)
if not "%RC%"=="0" exit /b %RC%
echo [run_ppe_auto_loop] idle sleep %SLEEP%s — Ctrl+C to stop
timeout /t %SLEEP% /nobreak >nul
goto loop
