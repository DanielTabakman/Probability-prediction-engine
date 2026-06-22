@echo off
setlocal
cd /d "%~dp0"
if exist ppe_operator_notify.local.cmd call ppe_operator_notify.local.cmd
python scripts\ppe_morning_report.py --repo-root "%CD%" --send-once
exit /b %ERRORLEVEL%
