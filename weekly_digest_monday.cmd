@echo off
setlocal

REM Monday morning: workflow radar (friction + orphan cleanup) then digest + notify.
REM Schedule weekly (e.g. Monday 04:00 local). Disable toasts: set PPE_NOTIFY=0

cd /d "%~dp0"
call "%~dp0workflow_radar.cmd" generate
if errorlevel 1 exit /b %ERRORLEVEL%
call "%~dp0weekly_digest.cmd" generate
if errorlevel 1 exit /b %ERRORLEVEL%
call "%~dp0weekly_digest.cmd" notify
exit /b %ERRORLEVEL%
