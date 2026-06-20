@echo off
setlocal
cd /d "%~dp0"
python scripts/run_pre_push_parity.py %*
exit /b %ERRORLEVEL%
