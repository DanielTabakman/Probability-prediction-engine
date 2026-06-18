@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
python "%CD%\scripts\ensure_ntfy_cmd_secret.py" --repo-root "%CD%"
exit /b %ERRORLEVEL%
