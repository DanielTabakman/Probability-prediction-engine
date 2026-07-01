@echo off
setlocal

REM One-shot: mark ready when build branch has commits, or trigger CLOSEOUT_ONLY run_ppe_local.
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\call_ppe_operator_local.cmd" call "%CD%\call_ppe_operator_local.cmd"
python "%CD%\scripts\ppe_post_build_watcher.py" --repo-root "%CD%" --finish-handoff
exit /b %ERRORLEVEL%
