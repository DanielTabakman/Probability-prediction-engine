@echo off
setlocal

REM Token economy audit — fixed overhead, starters, build-worker routing.
REM Usage:
REM   token_audit.cmd
REM   token_audit.cmd --stdout
REM   token_audit.cmd --prune-stale

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\ppe_token_audit.py" --repo-root "%CD%" %*
exit /b %ERRORLEVEL%
