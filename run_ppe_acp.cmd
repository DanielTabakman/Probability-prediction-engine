@echo off
setlocal
REM Full ACP relay (requires API credits and ppe-orchestrator-acp).
set "PPE_OPERATOR_PROFILE=acp"
call "%~dp0run_ppe.cmd" %*
exit /b %ERRORLEVEL%
