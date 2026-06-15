@echo off
setlocal

REM Register Task Scheduler: Monday workflow radar + weekly digest + phone ntfy push.
REM Run once from repo root. Delegates to install_weekly_radar_monday_task.cmd.

cd /d "%~dp0"
call "%~dp0install_weekly_radar_monday_task.cmd" %*
exit /b %ERRORLEVEL%
