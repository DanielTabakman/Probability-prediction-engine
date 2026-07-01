@echo off
setlocal

REM Phone buzzed? Opens Cursor + refreshes status. Normal path: operator thread → what's next?
cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\ppe_director_go.py" --repo-root "%CD%" %*
exit /b %ERRORLEVEL%
