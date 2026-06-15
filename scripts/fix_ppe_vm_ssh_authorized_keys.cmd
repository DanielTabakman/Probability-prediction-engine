@echo off
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0fix_ppe_vm_ssh_authorized_keys.ps1"
exit /b %ERRORLEVEL%
