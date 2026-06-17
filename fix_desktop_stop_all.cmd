@echo off
setlocal
REM Daily-driver PC: stop popup cmd windows + disable auto-start at logon.
REM Does NOT restart the loop (VM runs the loop).
REM Win+R:  C:\Users\USER\Desktop\Probability-prediction-engine\fix_desktop_stop_all.cmd

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

echo [fix_desktop_stop_all] stopping headless supervisor (if any)...
call "%CD%\run_ppe_headless_stack.cmd" --stop 2>nul

echo [fix_desktop_stop_all] removing logon scheduled task (PPE Desktop Operator)...
schtasks /Delete /TN "PPE Desktop Operator" /F >nul 2>&1

echo [fix_desktop_stop_all] stopping stray PPE python/cmd workers...
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq python.exe" /fo list ^| findstr /i "PID:"') do (
  wmic process where "ProcessId=%%a" get CommandLine 2>nul | findstr /i "Probability-prediction-engine" >nul
  if not errorlevel 1 taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq pythonw.exe" /fo list ^| findstr /i "PID:"') do (
  wmic process where "ProcessId=%%a" get CommandLine 2>nul | findstr /i "Probability-prediction-engine" >nul
  if not errorlevel 1 taskkill /PID %%a /F >nul 2>&1
)

echo.
echo [fix_desktop_stop_all] DONE.
echo   - Close any blank cmd windows still open (click X).
echo   - Desktop will NOT auto-start the operator at logon.
echo   - Loop belongs on the VM only. Use Cursor here for IDE BUILD slices.
echo   - Optional: setup_desktop_ide_only.cmd (blocks accidental loop on this PC)
exit /b 0
