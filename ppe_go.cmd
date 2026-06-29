@echo off
setlocal

REM Phone buzzed? Run this. Then Ctrl+V in a new Agent chat.
cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\ppe_director_go.py" --repo-root "%CD%" %*
exit /b %ERRORLEVEL%
