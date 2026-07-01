@echo off
REM Emergency only — copies build prompt to clipboard (overwrites clipboard).
cd /d "%~dp0"
set "PPE_IDE_HANDOFF_CLIPBOARD=1"
call "%~dp0DESKTOP_BUILD.cmd" %*
