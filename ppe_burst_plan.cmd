@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
python "%CD%\scripts\ppe_burst_plan.py" --repo-root "%CD%" %*
exit /b %ERRORLEVEL%
