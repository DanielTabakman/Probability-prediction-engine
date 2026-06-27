@echo off
setlocal

REM Clear stale Cursor CLI "out of usage" markers after plan resets.
REM Does not grant new quota — only unblocks headless dispatch heuristics.
REM See docs/SOP/PPE_TOKEN_ECONOMY_V1.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python -c "from pathlib import Path; from scripts.ppe_ide_handoff import clear_cli_usage_exhausted; clear_cli_usage_exhausted(Path('.')); print('OK: cleared stale Cursor CLI usage markers')"
exit /b %ERRORLEVEL%
