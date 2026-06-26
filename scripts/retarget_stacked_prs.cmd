@echo off
setlocal
cd /d "%~dp0.."
python "%CD%\scripts\retarget_stacked_prs.py" --repo-root "%CD%" --scan %*
exit /b %ERRORLEVEL%
