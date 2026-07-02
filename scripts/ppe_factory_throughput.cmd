@echo off
REM Factory throughput — slices/closeouts, phase stuck, supply.
setlocal
cd /d "%~dp0\.."
if exist "%CD%\ppe_operator_notify.local.cmd" call "%CD%\ppe_operator_notify.local.cmd"
set "PYTHONPATH=%CD%"
python "%CD%\scripts\ppe_factory_throughput.py" --write %*
exit /b %ERRORLEVEL%
