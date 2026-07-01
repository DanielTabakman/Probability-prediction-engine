@echo off
REM VM SSH reachability watchdog — schedule every 15m on desktop (not relay).
setlocal
cd /d "%~dp0\.."
if exist "%CD%\ppe_operator_notify.local.cmd" call "%CD%\ppe_operator_notify.local.cmd"
if exist "%CD%\ppe_operator_no_loop.local.cmd" call "%CD%\ppe_operator_no_loop.local.cmd"
set "PYTHONPATH=%CD%"
python "%CD%\scripts\ppe_network_watchdog.py" %*
exit /b %ERRORLEVEL%
