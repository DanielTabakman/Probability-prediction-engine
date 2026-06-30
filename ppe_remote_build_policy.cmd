@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
python "%CD%\scripts\ppe_remote_build_policy.py" %*
