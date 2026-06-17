@echo off
setlocal
REM Emergency stop popup storm + disable visible logon task. Does NOT restart.
REM Win+R:  C:\Users\ppeloop\Probability-prediction-engine\fix_vm_stop_all.cmd

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

echo [fix_vm_stop_all] stopping headless supervisor...
call "%CD%\run_ppe_headless_stack.cmd" --stop 2>nul

echo [fix_vm_stop_all] removing visible logon task (causes popup cmd windows)...
schtasks /Delete /TN "PPE Desktop Operator" /F >nul 2>&1

echo [fix_vm_stop_all] stopping stray PPE python workers...
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq python.exe" /fo list ^| findstr /i "PID:"') do (
  wmic process where "ProcessId=%%a" get CommandLine 2>nul | findstr /i "Probability-prediction-engine" >nul
  if not errorlevel 1 taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq pythonw.exe" /fo list ^| findstr /i "PID:"') do (
  wmic process where "ProcessId=%%a" get CommandLine 2>nul | findstr /i "Probability-prediction-engine" >nul
  if not errorlevel 1 taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq cmd.exe" /fo list ^| findstr /i "PID:"') do (
  wmic process where "ProcessId=%%a" get CommandLine 2>nul | findstr /i "Probability-prediction-engine run_ppe PPE auto loop watch_operator" >nul
  if not errorlevel 1 taskkill /PID %%a /F >nul 2>&1
)

echo.
echo [fix_vm_stop_all] DONE.
echo   - Close any blank cmd windows still open (click X).
echo   - Loop is STOPPED. Popups should NOT come back until you start headless again.
echo   - To start clean (no popups): fix_vm_headless.cmd
exit /b 0
