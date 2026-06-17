@echo off
REM === VM ONLY — double-click this file in File Explorer ===
REM Shows operator status. Window stays open.

cd /d "%~dp0"
call "%~dp0check_vm_loop.cmd" --no-pause
