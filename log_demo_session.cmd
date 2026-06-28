@echo off
setlocal
REM Log a demo session after showing MSOS (see /learn debrief or DEMO_OPERATOR_SCRIPT.md).
REM Example:
REM   log_demo_session.cmd --profile "options trader" --clarity Y --return Y --notes "NVDA dropped on monitor"

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
python "%CD%\scripts\log_demo_session.py" --append-validation-md %*
exit /b %ERRORLEVEL%
