@echo off
setlocal

REM One-time desktop setup for phone/loop auto-build (Cursor Agent CLI).
REM See docs/SOP/PPE_MOBILE_OPERATOR_V1.md

cd /d "%~dp0"

where agent >nul 2>&1
if %ERRORLEVEL%==0 (
  echo [setup_cursor_agent] agent already on PATH
  agent --version
  exit /b 0
)

if exist "%LOCALAPPDATA%\cursor-agent\agent.cmd" (
  echo [setup_cursor_agent] found %LOCALAPPDATA%\cursor-agent\agent.cmd
  echo Add to PATH or use verify_cursor_agent.cmd
  exit /b 0
)

echo [setup_cursor_agent] installing Cursor Agent CLI for Windows...
powershell -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://cursor.com/install?win32=true' | iex"
if errorlevel 1 (
  echo [setup_cursor_agent] install failed — see https://cursor.com/docs/cli/installation
  exit /b 1
)

echo [setup_cursor_agent] done — run: agent login
exit /b 0
