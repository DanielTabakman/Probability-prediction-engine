@echo off
set "PPE_OPERATOR_PROFILE=acp"
call "%~dp0run_ppe_auto.cmd" %*
exit /b %ERRORLEVEL%
