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
if exist "%CD%\ppe_operator_no_loop.local.cmd" (
  if not exist "%CD%\ppe_operator_no_loop.local.cmd.off-vm" (
    ren "%CD%\ppe_operator_no_loop.local.cmd" ppe_operator_no_loop.local.cmd.off-vm
    echo [setup_vm_loop_host] disabled daily-driver no_loop guard on this VM
  )
)
echo [setup_vm_loop_host] wrote %DEST%
type "%DEST%"
exit /b 0
