@echo off
setlocal
REM No API credits: local operator profile (deterministic relay, no steward API).
set "PPE_OPERATOR_PROFILE=local"
set "PPE_SKIP_ACP=1"
set "PPE_WORKER_MODE=deterministic"
call "%~dp0run_ppe_auto.cmd" %*
exit /b %ERRORLEVEL%
