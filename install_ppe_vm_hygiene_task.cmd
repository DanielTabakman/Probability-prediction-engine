@echo off
setlocal
REM VM loop host — schedule VM_HYGIENE.cmd weekly (worktree + git hygiene).

cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\scripts\install_ppe_vm_hygiene_task.ps1" -RepoRoot "%CD%"
pause
exit /b %ERRORLEVEL%
