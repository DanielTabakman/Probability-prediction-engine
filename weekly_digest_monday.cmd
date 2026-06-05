@echo off
setlocal

REM Monday reminder: refresh digest + Windows toast (Task Scheduler entry point).
REM Schedule weekly (e.g. Monday 09:00 local). Disable toasts: set PPE_NOTIFY=0

cd /d "%~dp0"
call "%~dp0weekly_digest.cmd" generate
if errorlevel 1 exit /b %ERRORLEVEL%
call "%~dp0weekly_digest.cmd" notify
exit /b %ERRORLEVEL%
