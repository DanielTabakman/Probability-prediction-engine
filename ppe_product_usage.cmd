@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
python "%CD%\scripts\ppe_product_usage.py" --repo-root "%CD%" %*
exit /b %ERRORLEVEL%
