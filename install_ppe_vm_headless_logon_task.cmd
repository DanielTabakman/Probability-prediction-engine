@echo off
setlocal
REM VM loop host only — register Task Scheduler to run headless stack at user logon.
REM Double-click once on the VM (as ppeloop). See docs/SOP/PPE_VM_LOOP_HOST_V1.md Phase 6.

cd /d "%~dp0"
if not exist "%CD%\ppe_operator_loop_host.local.cmd" (
  if exist "%CD%\setup_vm_loop_host.cmd" call "%CD%\setup_vm_loop_host.cmd"
)

echo [install_ppe_vm_headless_logon_task] registering logon task...
powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\scripts\install_ppe_vm_headless_logon_task.ps1" -RepoRoot "%CD%"
set "RC=%ERRORLEVEL%"
if errorlevel 1 goto done

echo.
echo [install_ppe_vm_headless_logon_task] ensuring stack now (smoke test)...
call "%CD%\run_ppe_headless_stack.cmd" --ensure

:done
echo.
pause
exit /b %RC%
