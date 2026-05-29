@echo off
REM No credits: deterministic relay; build PRODUCT slices in Cursor IDE chat.
set "PPE_OPERATOR_PROFILE=local"
call "%~dp0run_ppe.cmd" %*
exit /b %ERRORLEVEL%
