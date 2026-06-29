@echo off
setlocal
REM One-shot warm or loop host for display cache refresh sidecar alternative on Windows.
REM Usage: run_display_cache_refresh.cmd
REM        run_display_cache_refresh.cmd --loop

cd /d "%~dp0"
set "BASE=%PPE_DISPLAY_API_BASE_URL%"
if not defined BASE set "BASE=http://127.0.0.1:8765"
python scripts\run_display_cache_refresh.py --base-url "%BASE%" %*
exit /b %ERRORLEVEL%
