@echo off
setlocal

REM Mobile operator watch — ntfy push on verdict change or loop death.
REM Usage:
REM   watch_operator_mobile.cmd
REM   watch_operator_mobile.cmd --once
REM   watch_operator_mobile.cmd --interval 60
REM Requires PPE_NTFY_TOPIC — see docs/SOP/PPE_MOBILE_OPERATOR_V1.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

if exist "%CD%\ppe_operator_local.cmd" call "%CD%\ppe_operator_local.cmd"

if /i "%~1"=="--once" (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\scripts\watch_operator_mobile.ps1" -RepoRoot "%CD%" -Once
  exit /b %ERRORLEVEL%
)

set "INTERVAL=120"
if /i "%~1"=="--interval" set "INTERVAL=%~2"

powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\scripts\watch_operator_mobile.ps1" -RepoRoot "%CD%" -IntervalSeconds %INTERVAL%
exit /b %ERRORLEVEL%
