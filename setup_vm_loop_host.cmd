@echo off
setlocal
REM One-time VM setup: create ppe_operator_loop_host.local.cmd (gitignored).
REM Win+R:  C:\Users\ppeloop\Probability-prediction-engine\setup_vm_loop_host.cmd

cd /d "%~dp0"
set "DEST=%CD%\ppe_operator_loop_host.local.cmd"
set "SRC=%CD%\ppe_operator_loop_host.local.cmd.example"

if not exist "%SRC%" (
  echo [setup_vm_loop_host] missing %SRC%
  exit /b 1
)

copy /Y "%SRC%" "%DEST%" >nul
echo [setup_vm_loop_host] wrote %DEST%
type "%DEST%"
exit /b 0
