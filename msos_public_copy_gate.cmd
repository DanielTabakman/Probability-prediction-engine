@echo off
setlocal
cd /d "%~dp0.."
python scripts\msos_public_copy_gate.py %*
exit /b %ERRORLEVEL%
