@echo off
setlocal
cd /d "%~dp0"
python scripts\ppe_branch_recovery.py %*
