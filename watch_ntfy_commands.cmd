@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_local.cmd" call "%CD%\ppe_operator_local.cmd"

REM Restart the listener if Python exits (crash, network blip, etc.).
REM Without this loop the cmd window stays open but stops responding to phone commands.
:listen_loop
python "%CD%\scripts\ppe_ntfy_listen.py" --repo-root "%CD%"
set "RC=%ERRORLEVEL%"
if "%RC%"=="0" exit /b 0
echo ppe_ntfy_listen: exited code %RC% — restarting in 5s...
timeout /t 5 /nobreak >nul
goto listen_loop
