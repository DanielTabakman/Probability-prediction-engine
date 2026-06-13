@echo off
setlocal

REM PPE autobuilder — unified status, diagnose, and pipeline actions.
REM Usage:
REM   ppe_autobuilder.cmd status [--json] [--brief] [--write]
REM   ppe_autobuilder.cmd diagnose [--json]
REM   ppe_autobuilder.cmd ensure
REM   ppe_autobuilder.cmd advance
REM   ppe_autobuilder.cmd retry-build
REM   ppe_autobuilder.cmd handoff
REM   ppe_autobuilder.cmd finish-pending
REM   ppe_autobuilder.cmd run-local
REM Agent: @ppe-autobuilder-operator — see docs/SOP/PPE_AUTOBUILDER_V1.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_local.cmd" call "%CD%\ppe_operator_local.cmd"
set "PPE_OPERATOR_PROFILE=local"

python "%CD%\scripts\ppe_operator_env.py"
if errorlevel 1 exit /b 1

if "%~1"=="" (
  python "%CD%\scripts\ppe_autobuilder.py" --repo-root "%CD%" status --write --brief
  exit /b %ERRORLEVEL%
)

python "%CD%\scripts\ppe_autobuilder.py" --repo-root "%CD%" %*
exit /b %ERRORLEVEL%
