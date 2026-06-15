@echo off
setlocal

REM Desktop operator stack entry — headless (default in local profile) or legacy cmd windows.
REM Prefer run_ppe_desktop_operator.cmd (queue + stack ensure + status).
REM See docs/SOP/PPE_HEADLESS_STACK_V1.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

call "%~dp0call_ppe_operator_local.cmd"

python -c "from pathlib import Path; from scripts.ppe_operator_config import headless_stack_mode; raise SystemExit(0 if headless_stack_mode(Path('.')) else 1)"
if not errorlevel 1 (
  echo [start_ppe_desktop_operator] headless mode — starting detached supervisor
  call "%~dp0run_ppe_headless_stack.cmd" --ensure
  exit /b %ERRORLEVEL%
)

start "PPE auto loop" cmd /k call "%~dp0run_ppe_auto_local_loop.cmd"
timeout /t 3 /nobreak >nul
start "PPE mobile watch" cmd /k call "%~dp0watch_operator_mobile.cmd"
timeout /t 2 /nobreak >nul
start "PPE ntfy commands" cmd /k call "%~dp0watch_ntfy_commands.cmd"
timeout /t 2 /nobreak >nul
start "PPE IDE BUILD watcher" cmd /k call "%~dp0watch_ide_build_local.cmd"

echo Started legacy windowed stack (4 cmd windows).
echo Prefer headless: set desktopStack.mode=headless in docs/SOP/PPE_AUTO_OPERATOR.local.json
exit /b 0
