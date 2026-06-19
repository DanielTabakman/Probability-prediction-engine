@echo off
setlocal
cd /d "%~dp0"
if exist "%~dp0ppe_operator_ssh.local.cmd" call "%~dp0ppe_operator_ssh.local.cmd"
python scripts/ppe_vps_ssh.py %*
