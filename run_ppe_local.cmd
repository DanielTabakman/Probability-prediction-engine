@echo off
setlocal enabledelayedexpansion

REM Single chapter / phase run with local profile (no ACP). Use after IDE product BUILD.
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
set "PPE_OPERATOR_PROFILE=local"

python "%CD%\scripts\ppe_operator_env.py"
if errorlevel 1 exit /b 1

call "%CD%\run_ppe.cmd" %*
exit /b %ERRORLEVEL%
