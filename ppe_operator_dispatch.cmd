@echo off
setlocal
REM Execute burst direct_action (opt-in: set PPE_AUTO_DISPATCH=1).
REM   ppe_operator_dispatch.cmd --from-burst-plan
REM   ppe_operator_dispatch.cmd --action "DESKTOP_CONTINUE.cmd --no-pause" --force

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_no_loop.local.cmd" call "%CD%\ppe_operator_no_loop.local.cmd"

python "%CD%\scripts\ppe_operator_dispatch.py" --repo-root "%CD%" %*
exit /b %ERRORLEVEL%
