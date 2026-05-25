@echo off
cd /d "%~dp0"
set "PATH=%ProgramFiles%\nodejs;%PATH%"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\auth_google_docs_mcp.ps1"
if errorlevel 1 pause
