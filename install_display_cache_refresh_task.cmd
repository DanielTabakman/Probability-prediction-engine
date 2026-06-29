@echo off
setlocal
REM Register repeating display cache warm (VPS / loop host without compose sidecar).
REM Usage: install_display_cache_refresh_task.cmd
REM        install_display_cache_refresh_task.cmd --unregister

cd /d "%~dp0"
set "PS_ARGS=-RepoRoot ""%CD%"""
if /i "%~1"=="--unregister" set "PS_ARGS=%PS_ARGS% -Unregister"

powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\scripts\install_ppe_display_cache_refresh_task.ps1" %PS_ARGS%
exit /b %ERRORLEVEL%
