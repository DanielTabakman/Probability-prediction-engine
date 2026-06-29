@echo off
REM Regenerate MSOS module map HTML from PPE_MODULE_REGISTRY.json
python scripts\render_msos_module_map.py --write
if errorlevel 1 exit /b 1
echo Open: docs\SOP\assets\msos_module_map.html
