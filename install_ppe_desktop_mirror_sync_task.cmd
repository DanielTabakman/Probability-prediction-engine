@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\scripts\install_ppe_desktop_mirror_sync_task.ps1" -RepoRoot "%CD%" %*
exit /b %ERRORLEVEL%
