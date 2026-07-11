@echo off
setlocal
set "REPO=%~dp0"
python "%REPO%scripts\ppe_autobuilder_pr_cleanup.py" --repo "%REPO%" %*
exit /b %ERRORLEVEL%
