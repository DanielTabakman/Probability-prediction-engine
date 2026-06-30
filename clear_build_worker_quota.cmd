@echo off
setlocal

REM Clear stale Cursor/Codex CLI "out of usage" markers after plan resets.
REM Does not grant new quota — only unblocks headless dispatch heuristics.
REM See docs/SOP/PPE_TOKEN_ECONOMY_V1.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python -c "from pathlib import Path; from scripts.ppe_ide_handoff import clear_build_worker_quota; clear_build_worker_quota(Path('.')); print('OK: cleared stale Cursor/Codex CLI usage markers')"
exit /b %ERRORLEVEL%
