@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
python "%CD%\scripts\ppe_notify_setup.py" --repo-root "%CD%" %*
exit /b %ERRORLEVEL%
