@echo off
setlocal

REM Token economy audit + monitor. See docs/SOP/PPE_TOKEN_ECONOMY_MONITOR_V1.md
REM   token_audit.cmd
REM   token_audit.cmd --prune-stale
REM   token_audit.cmd --fail-on-watch

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\ppe_token_audit.py" --repo-root "%CD%" %*
exit /b %ERRORLEVEL%
