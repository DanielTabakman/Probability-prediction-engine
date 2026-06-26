@echo off
setlocal
cd /d "%~dp0"
python scripts\msos_journey_crawler.py %*
