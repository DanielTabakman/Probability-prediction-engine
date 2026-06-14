@echo off
setlocal

REM Local IDE BUILD trigger watcher — polls .cursor\IDE_BUILD_TRIGGER.json and starts agent CLI.
REM See docs/SOP/CURSOR_IDE_BUILD_AUTOMATION_V1.md
REM Usage:
REM   watch_ide_build_local.cmd
REM   watch_ide_build_local.cmd --once

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

if exist "%CD%\ppe_operator_local.cmd" call "%CD%\ppe_operator_local.cmd"

if /i "%~1"=="--once" (
  python "%CD%\scripts\ppe_ide_build_local_watcher.py" --repo-root "%CD%" --once
  exit /b %ERRORLEVEL%
)

python "%CD%\scripts\ppe_ide_build_local_watcher.py" --repo-root "%CD%"
exit /b %ERRORLEVEL%
