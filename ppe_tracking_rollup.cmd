@echo off
setlocal

REM In-house tracking rollup (HTML) — replaces external spreadsheet ritual.
REM Regenerates TRACKING_ROLLUP.html via ppe_tracking_status.

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

call "%~dp0ppe_tracking_status.cmd" %*
if errorlevel 1 exit /b %ERRORLEVEL%

echo ppe_tracking_rollup: open artifacts\control_plane\TRACKING_ROLLUP.html
exit /b 0
