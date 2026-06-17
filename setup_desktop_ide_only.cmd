@echo off
setlocal
REM One-time daily-driver setup: block loop on this PC (VM is loop host).
REM Win+R:  C:\Users\USER\Desktop\Probability-prediction-engine\setup_desktop_ide_only.cmd

cd /d "%~dp0"
set "SRC=%CD%\ppe_operator_no_loop.local.cmd.example"
set "DEST=%CD%\ppe_operator_no_loop.local.cmd"
set "LOOP_HOST=%CD%\ppe_operator_loop_host.local.cmd"

if not exist "%SRC%" (
  echo [setup_desktop_ide_only] missing %SRC%
  exit /b 1
)

copy /Y "%SRC%" "%DEST%" >nul
echo [setup_desktop_ide_only] wrote %DEST%

if exist "%LOOP_HOST%" (
  del /F "%LOOP_HOST%" >nul 2>&1
  echo [setup_desktop_ide_only] removed %LOOP_HOST% (VM-only file was on this PC)
)

echo [setup_desktop_ide_only] removing logon task if present...
schtasks /Delete /TN "PPE Desktop Operator" /F >nul 2>&1

echo.
echo [setup_desktop_ide_only] ok — this PC is IDE BUILD only; loop runs on the VM.
type "%DEST%"
exit /b 0
