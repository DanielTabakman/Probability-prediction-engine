@echo off
setlocal

REM Register Task Scheduler: run PPE desktop operator at user logon.
REM Run once from repo root (Admin not required for current-user logon task).

cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\scripts\install_ppe_desktop_operator_task.ps1" -RepoRoot "%CD%"
exit /b %ERRORLEVEL%
