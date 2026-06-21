@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
python "%CD%\scripts\msos_production_playwright_witness.py" --write-dir "%CD%\artifacts\health\msos_production_playwright"
exit /b %ERRORLEVEL%
