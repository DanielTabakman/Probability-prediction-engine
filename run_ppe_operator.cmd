@echo off
setlocal

REM Operator status: verdict + next commands before auto-loop or IDE BUILD.
REM Usage:
REM   run_ppe_operator.cmd
REM   run_ppe_operator.cmd --brief
REM   run_ppe_operator.cmd --notify
REM   run_ppe_operator.cmd --json

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
set "PPE_OPERATOR_PROFILE=local"

python "%CD%\scripts\ppe_operator_env.py"
if errorlevel 1 exit /b 1

python "%CD%\scripts\ppe_operator_status.py" --repo-root "%CD%" %*
exit /b %ERRORLEVEL%
