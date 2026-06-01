@echo off
setlocal
REM No API credits: local operator profile (deterministic relay, no steward API).
set "PPE_OPERATOR_PROFILE=local"
call "%~dp0run_ppe_auto.cmd" %*
exit /b %ERRORLEVEL%
