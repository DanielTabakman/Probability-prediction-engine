@echo off
setlocal

REM Monday prep: autoclean + easy autofix (scheduled ~2h before report).
REM Usage: monday_morning_prep.cmd [prep|wait]

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_local.cmd" call "%CD%\ppe_operator_local.cmd"

set "SUBCMD=prep"
if not "%~1"=="" set "SUBCMD=%~1"

python "%CD%\scripts\ppe_monday_morning_prep.py" --repo-root "%CD%" %SUBCMD%
exit /b %ERRORLEVEL%
