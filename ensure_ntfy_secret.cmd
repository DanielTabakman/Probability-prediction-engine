@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
python "%CD%\scripts\bootstrap_operator_notify_secret.py" --repo-root "%CD%"
exit /b %ERRORLEVEL%
