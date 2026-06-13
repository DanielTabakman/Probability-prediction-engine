@echo off
setlocal
cd /d "%~dp0"
call "%~dp0steward_nudge.cmd" wednesday
exit /b %ERRORLEVEL%
