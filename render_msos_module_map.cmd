@echo off
REM Regenerate only (no browser). To refresh + open: OPEN_MODULE_MAP.cmd
cd /d "%~dp0"
python scripts\render_msos_module_map.py --write
exit /b %ERRORLEVEL%
