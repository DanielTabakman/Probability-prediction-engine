@echo off
setlocal
cd /d "%~dp0\.."
set "PYTHONPATH=%CD%"
python "%CD%\scripts\verify_vm_phase_mirror.py" --repo-root "%CD%" %*
exit /b %ERRORLEVEL%
