@echo off
setlocal
cd /d "%~dp0"
python scripts/sop_discovery_maintenance.py %*
