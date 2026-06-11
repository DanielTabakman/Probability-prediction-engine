@echo off
setlocal

REM One-shot: if next pending product slice has build-branch commits, mark + run_ppe_local.
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
python "%CD%\scripts\ppe_post_build_watcher.py" --repo-root "%CD%"
exit /b %ERRORLEVEL%
