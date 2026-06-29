@echo off
REM Refresh + open MSOS module map (double-click or say "open the dashboard" in Cursor).
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
python scripts\ppe_operator_shortcuts.py --repo-root "%CD%" --apply --quiet 2>nul
python scripts\open_msos_module_map.py
exit /b %ERRORLEVEL%
