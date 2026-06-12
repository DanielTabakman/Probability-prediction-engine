@echo off
setlocal

REM Diagnose IDE BUILD automation — which part is broken (quota vs wiring).
REM Exit 0 OK | 1 broken | 2 quota only (retry later).
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_local.cmd" call "%CD%\ppe_operator_local.cmd"

python "%CD%\scripts\ppe_ide_build_automation_health.py" --repo-root "%CD%"
exit /b %ERRORLEVEL%
