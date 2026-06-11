@echo off
setlocal enabledelayedexpansion

REM Repeat run_ppe_auto until you stop it (Ctrl+C). Sleep between passes when idle.
REM idleSleepSeconds from docs/SOP/PPE_AUTO_OPERATOR.json (default 120).
REM Exit 7: guard stop — notify, then sleep+retry when keepLoopAliveOnGuardStop is true.

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_local.cmd" call "%CD%\ppe_operator_local.cmd"
if not defined PPE_OPERATOR_PROFILE set "PPE_OPERATOR_PROFILE=local"

python "%CD%\scripts\ppe_operator_env.py"
if errorlevel 1 exit /b 1

set "SLEEP=120"
for /f "usebackq delims=" %%s in (`python -c "from pathlib import Path; from scripts.ppe_operator_config import idle_sleep_seconds; print(idle_sleep_seconds(Path('.')))"`) do set "SLEEP=%%s"

echo [run_ppe_auto_loop] startup hygiene (queue/backlog repair + health audit)
python "%CD%\scripts\run_codebase_health_gate.py" --repo-root "%CD%" --skip-relay
if errorlevel 1 (
  echo [run_ppe_auto_loop] health gate failed — fix queue/backlog drift before continuing
  exit /b 1
)

echo [run_ppe_auto_loop] startup preflight
python "%CD%\scripts\ppe_operator_status.py" --repo-root "%CD%"
set "PREFLIGHT_RC=%ERRORLEVEL%"
if "%PREFLIGHT_RC%"=="7" goto handle_guard_stop
if not "%PREFLIGHT_RC%"=="0" exit /b %PREFLIGHT_RC%

echo [run_ppe_auto_loop] git sync pull
python "%CD%\scripts\ppe_operator_git_sync.py" --repo-root "%CD%" --pull
python "%CD%\scripts\ppe_operator_git_sync.py" --repo-root "%CD%" --auto-publish

:loop
echo [run_ppe_auto_loop] starting pass at %DATE% %TIME%
python "%CD%\scripts\ppe_operator_git_sync.py" --repo-root "%CD%" --pull
python "%CD%\scripts\ppe_operator_git_sync.py" --repo-root "%CD%" --auto-publish
python "%CD%\scripts\ppe_operator_status.py" --repo-root "%CD%" --brief --no-write
set "STATUS_RC=%ERRORLEVEL%"
if "%STATUS_RC%"=="7" goto handle_guard_stop
call "%~dp0run_ppe_auto.cmd"
set "RC=%ERRORLEVEL%"
if "%RC%"=="7" goto handle_guard_stop
if not "%RC%"=="0" exit /b %RC%
echo [run_ppe_auto_loop] idle sleep %SLEEP%s — Ctrl+C to stop
timeout /t %SLEEP% /nobreak >nul
goto loop

:handle_guard_stop
python "%CD%\scripts\ppe_operator_status.py" --repo-root "%CD%" --notify
for /f "usebackq delims=" %%g in (`python "%CD%\scripts\ppe_loop_guard_stop.py" --repo-root "%CD%"`) do set "GUARD_SLEEP=%%g"
if "!GUARD_SLEEP!"=="-1" (
  echo [run_ppe_auto_loop] guard stop — review artifacts/orchestrator/OPERATOR_STATUS.md
  exit /b 7
)
echo [run_ppe_auto_loop] guard stop — sleeping !GUARD_SLEEP!s then retry (keepLoopAliveOnGuardStop)
timeout /t !GUARD_SLEEP! /nobreak >nul
goto loop
