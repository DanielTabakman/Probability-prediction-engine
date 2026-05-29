@echo off
REM With credits: full ACP orchestrator (requires CURSOR_API_KEY + ppe-orchestrator-acp).
set "PPE_OPERATOR_PROFILE=acp"
call "%~dp0run_ppe.cmd" %*
exit /b %ERRORLEVEL%
