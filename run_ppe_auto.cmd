@echo off
setlocal enabledelayedexpansion

REM Auto-operator entry: continuous queue drain + backlog propagation + steward charter.
REM Requires docs/SOP/PPE_AUTO_OPERATOR.json with "enabled": true.
REM Optional: CURSOR_API_KEY when stewardCharter is true (Cursor SDK local runtime).

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\ppe_operator_env.py"
if errorlevel 1 exit /b 1

set "MAX_CH=20"
for /f "usebackq delims=" %%m in (`python "%CD%\scripts\ppe_operator_env.py" --print-continuous-max`) do set "MAX_CH=%%m"

call "%CD%\run_ppe.cmd" --continuous --continuous-max %MAX_CH% %*
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" exit /b %RC%
exit /b 0
