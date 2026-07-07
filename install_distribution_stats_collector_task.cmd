@echo off
setlocal
REM Compatibility wrapper for the daily distribution stats collector task.
REM Usage: install_distribution_stats_collector_task.cmd
REM        install_distribution_stats_collector_task.cmd --unregister

cd /d "%~dp0"
call "%CD%\install_distribution_collector_task.cmd" %*
exit /b %ERRORLEVEL%
