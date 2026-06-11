@echo off
setlocal

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\desktop_operator_preflight.py" --repo-root "%CD%" --agent-only
exit /b %ERRORLEVEL%
