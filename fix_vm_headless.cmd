@echo off
setlocal
REM Stop popup cmd windows and run the loop headless (logs only, no new windows).
REM Usage on VM:  Win+R  then  C:\Users\ppeloop\Probability-prediction-engine\fix_vm_headless.cmd

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if not exist "%CD%\ppe_operator_loop_host.local.cmd" (
  if exist "%CD%\ppe_operator_loop_host.local.cmd.example" (
    copy /Y "%CD%\ppe_operator_loop_host.local.cmd.example" "%CD%\ppe_operator_loop_host.local.cmd" >nul
  )
)
call "%CD%\call_ppe_operator_local.cmd" 2>nul
call "%CD%\ppe_operator_loop_host.local.cmd" 2>nul
set "PPE_OPERATOR_PROFILE=local"
set "PPE_SKIP_ACP=1"
set "PPE_STACK_HEADLESS=1"

echo [fix_vm_headless] stopping any visible stack first...
call "%CD%\fix_vm_stop_all.cmd"
if errorlevel 1 exit /b %ERRORLEVEL%

echo [fix_vm_headless] starting headless stack (no popup windows)...
call "%CD%\run_ppe_headless_stack.cmd" --ensure
if errorlevel 1 exit /b %ERRORLEVEL%

echo [fix_vm_headless] ok — logs under artifacts\orchestrator\HEADLESS_STACK_*.log
echo [fix_vm_headless] status: ppe_autobuilder.cmd status --brief
exit /b 0
