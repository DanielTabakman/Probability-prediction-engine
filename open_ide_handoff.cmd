@echo off
setlocal

REM Open IDE handoff for the current IDE_BUILD product slice (no headless CLI).
cd /d "%~dp0"
set "PYTHONPATH=%CD%"

if exist "%CD%\ppe_operator_local.cmd" call "%CD%\ppe_operator_local.cmd"
set "PPE_OPERATOR_PROFILE=local"

python "%CD%\scripts\ppe_operator_env.py"
if errorlevel 1 exit /b 1

python "%CD%\scripts\ppe_ide_handoff.py" --repo-root "%CD%" --respond --force-handoff
exit /b %ERRORLEVEL%
