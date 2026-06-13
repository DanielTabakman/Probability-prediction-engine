@echo off
setlocal
cd /d "%~dp0"
call "%~dp0steward_nudge.cmd" monday
exit /b %ERRORLEVEL%
