@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
python "%CD%\scripts\research_status.py" %*
exit /b %ERRORLEVEL%
