@echo off
set "PPE_OPERATOR_PROFILE=local"
call "%~dp0run_ppe_auto_loop.cmd" %*
exit /b %ERRORLEVEL%
