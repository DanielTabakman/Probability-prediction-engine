@echo off
setlocal

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
set "PPE_OPERATOR_PROFILE=local"

python "%CD%\scripts\desktop_operator_preflight.py" --repo-root "%CD%" --codex-only
exit /b %ERRORLEVEL%
