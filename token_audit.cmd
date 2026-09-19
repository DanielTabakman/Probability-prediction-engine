@echo off
setlocal

REM Token economy audit + monitor. See docs/SOP/PPE_TOKEN_ECONOMY_MONITOR_V1.md
REM   token_audit.cmd
REM   token_audit.cmd --prune-stale
REM   token_audit.cmd --fail-on-watch

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\ppe_token_audit.py" --repo-root "%CD%" %*
set "CURSOR_AUDIT_EXIT=%ERRORLEVEL%"

python "%CD%\scripts\ppe_context_surface_audit.py" --repo-root "%CD%" %*
set "CONTEXT_AUDIT_EXIT=%ERRORLEVEL%"

if not "%CURSOR_AUDIT_EXIT%"=="0" exit /b %CURSOR_AUDIT_EXIT%
exit /b %CONTEXT_AUDIT_EXIT%
