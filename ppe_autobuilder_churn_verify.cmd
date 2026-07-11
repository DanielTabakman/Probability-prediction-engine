@echo off
setlocal
set "REPO=%~dp0"
python "%REPO%scripts\ppe_autobuilder_churn_verify.py" --repo "%REPO%" %*
exit /b %ERRORLEVEL%
