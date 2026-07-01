@echo off
setlocal
REM Daily desktop — schedule VM SSH reachability watchdog (not relay).

cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\scripts\install_ppe_network_watchdog_task.ps1" -RepoRoot "%CD%" %*
if not "%~1"=="" exit /b %ERRORLEVEL%
pause
exit /b %ERRORLEVEL%
