@echo off
REM Emergency only — copies director prompt to clipboard (overwrites clipboard).
cd /d "%~dp0"
set "PPE_IDE_HANDOFF_CLIPBOARD=1"
call "%~dp0ppe_go.cmd" %*
