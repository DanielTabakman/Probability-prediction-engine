@echo off
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_ppe_vm_cursor_ssh.ps1"
exit /b %ERRORLEVEL%
