@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
python "%CD%\scripts\msos_production_demo_witness.py" --write "%CD%\artifacts\health\msos_production_demo_witness.json"
exit /b %ERRORLEVEL%
