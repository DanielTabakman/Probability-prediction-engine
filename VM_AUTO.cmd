@echo off
REM === VM ONLY — this is your "auto" button. Same as VM_RESTART. ===
REM Pull + stop + wait + start headless loop. No popups on your real PC.

cd /d "%~dp0"
call "%~dp0VM_RESTART.cmd"
