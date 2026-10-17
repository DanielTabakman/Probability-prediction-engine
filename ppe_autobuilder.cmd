@echo off
setlocal

REM PPE autobuilder — unified status, diagnose, and pipeline actions.
REM Usage:
REM   ppe_autobuilder.cmd status [--json] [--brief] [--write]
REM   ppe_autobuilder.cmd diagnose [--json]
REM   ppe_autobuilder.cmd ensure
REM   ppe_autobuilder.cmd advance [--allow-budget-watch "reason"]
REM   ppe_autobuilder.cmd retry-build [--allow-budget-watch "reason"]
REM   ppe_autobuilder.cmd handoff [--allow-budget-watch "reason"]
REM   ppe_autobuilder.cmd finish-pending
REM   ppe_autobuilder.cmd run-local
REM   ppe_autobuilder.cmd reconcile [--dry-run] [--json]
REM Agent: @ppe-autobuilder-operator — see docs/SOP/PPE_AUTOBUILDER_V1.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_local.cmd" call "%CD%\ppe_operator_local.cmd"
set "PPE_OPERATOR_PROFILE=local"

python "%CD%\scripts\ppe_operator_env.py"
if errorlevel 1 exit /b 1

if "%~1"=="" (
  python -u "%CD%\scripts\ppe_autobuilder.py" --repo-root "%CD%" status --write --brief
  exit /b %ERRORLEVEL%
)

if /I "%~1"=="retry-build" goto :gated_dispatch
if /I "%~1"=="handoff" goto :gated_dispatch
if /I "%~1"=="advance" goto :gated_dispatch

goto :run_standard

:gated_dispatch
set "PPE_GATE_ACTION=%~1"
if "%~2"=="" goto :run_gate
if /I not "%~2"=="--allow-budget-watch" (
  echo ppe_autobuilder: unsupported dispatch argument "%~2"
  echo Usage: ppe_autobuilder.cmd %PPE_GATE_ACTION% [--allow-budget-watch "reason"]
  exit /b 2
)
if "%~3"=="" (
  echo ppe_autobuilder: --allow-budget-watch requires a non-empty reason
  exit /b 2
)
if not "%~4"=="" (
  echo ppe_autobuilder: unexpected extra dispatch argument "%~4"
  exit /b 2
)
python -u "%CD%\scripts\ppe_billing_gate.py" --repo-root "%CD%" --command "%PPE_GATE_ACTION%" --allow-watch --watch-reason "%~3"
if errorlevel 1 exit /b 2
goto :run_gated_action

:run_gate
python -u "%CD%\scripts\ppe_billing_gate.py" --repo-root "%CD%" --command "%PPE_GATE_ACTION%"
if errorlevel 1 exit /b 2

:run_gated_action
python -u "%CD%\scripts\ppe_autobuilder.py" --repo-root "%CD%" "%PPE_GATE_ACTION%"
exit /b %ERRORLEVEL%

:run_standard
python -u "%CD%\scripts\ppe_autobuilder.py" --repo-root "%CD%" %*
exit /b %ERRORLEVEL%
