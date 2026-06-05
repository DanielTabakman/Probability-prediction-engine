@echo off
setlocal
REM Long-running local auto-operator (no ACP). Ctrl+C to stop.
set "PPE_OPERATOR_PROFILE=local"
set "PPE_SKIP_ACP=1"
set "PPE_WORKER_MODE=deterministic"
call "%~dp0run_ppe_auto_loop.cmd" %*
exit /b %ERRORLEVEL%
