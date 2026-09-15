@echo off
REM Host PC — start PPE-Loop-Host and set it to start when Windows boots.
REM Double-click; accepts UAC.

net session >nul 2>&1
if errorlevel 1 (
  echo Requesting Administrator for Hyper-V Start-VM / Set-VM...
  powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b 0
)

cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start_ppe_loop_host_vm.ps1"
set "RC=%ERRORLEVEL%"
echo.
pause
exit /b %RC%
