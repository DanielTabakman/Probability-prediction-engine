@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
python "%CD%\scripts\ppe_context_window_closeout.py" --repo-root "%CD%" %*
exit /b %ERRORLEVEL%
