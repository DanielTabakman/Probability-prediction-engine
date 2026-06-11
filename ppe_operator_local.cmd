@echo off
REM Load gitignored operator secrets/env (ntfy, git identity, optional GH_TOKEN).
REM Called by loop entrypoints — see docs/SOP/DESKTOP_OPERATOR_SETUP_STARTER.md

if exist "%LOCALAPPDATA%\cursor-agent" set "PATH=%LOCALAPPDATA%\cursor-agent;%PATH%"
if exist "%~dp0ppe_operator_cursor.local.cmd" call "%~dp0ppe_operator_cursor.local.cmd"
if exist "%~dp0ppe_operator_notify.local.cmd" call "%~dp0ppe_operator_notify.local.cmd"
if exist "%~dp0ppe_operator_git.local.cmd" call "%~dp0ppe_operator_git.local.cmd"
