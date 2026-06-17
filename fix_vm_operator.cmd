@echo off
setlocal
REM VM loop-host recovery — delegates to vm_bootstrap --recover (manifest-aware).
REM Usage (on VM):  fix_vm_operator.cmd

cd /d "%~dp0"
call "%~dp0vm_bootstrap.cmd" --recover
exit /b %ERRORLEVEL%
