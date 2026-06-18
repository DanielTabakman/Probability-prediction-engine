@echo off
setlocal
REM Emergency stop operator stack on the daily PC. Does NOT restart the VM loop.
REM See docs/SOP/PPE_VM_DESKTOP_OPERATOR_HANDOFF.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

echo [fix_desktop_stop_all] ensuring daily-driver guards...
if not exist "%CD%\ppe_operator_no_loop.local.cmd" (
  if exist "%CD%\ppe_operator_no_loop.local.cmd.example" (
    copy /Y "%CD%\ppe_operator_no_loop.local.cmd.example" "%CD%\ppe_operator_no_loop.local.cmd" >nul
    echo   created ppe_operator_no_loop.local.cmd
  )
)

echo [fix_desktop_stop_all] disabling phone command listener on daily PC...
if exist "%CD%\ppe_operator_no_loop.local.cmd" (
  findstr /i /c:"PPE_NTFY_CMD_ENABLED=0" "%CD%\ppe_operator_no_loop.local.cmd" >nul 2>&1
  if errorlevel 1 (
    echo set "PPE_NTFY_CMD_ENABLED=0" >> "%CD%\ppe_operator_no_loop.local.cmd"
    echo   appended PPE_NTFY_CMD_ENABLED=0
  )
)

echo [fix_desktop_stop_all] stopping headless supervisor (if any)...
if exist "%CD%\run_ppe_headless_stack.cmd" call "%CD%\run_ppe_headless_stack.cmd" --stop 2>nul

echo [fix_desktop_stop_all] stopping desktop auto-operator...
if exist "%CD%\scripts\ppe_desktop_auto_operator.py" (
  python "%CD%\scripts\ppe_desktop_auto_operator.py" --repo-root "%CD%" --stop 2>nul
)

echo [fix_desktop_stop_all] removing legacy logon tasks...
schtasks /Delete /TN "PPE Desktop Operator" /F >nul 2>&1
schtasks /Delete /TN "PPE Desktop Operator Watchdog" /F >nul 2>&1
schtasks /Delete /TN "PPE Headless Stack" /F >nul 2>&1

echo [fix_desktop_stop_all] stopping stray PPE workers...
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq python.exe" /fo list ^| findstr /i "PID:"') do (
  wmic process where "ProcessId=%%a" get CommandLine 2>nul | findstr /i "Probability-prediction-engine ppe_ntfy_listen ppe_watch_operator ppe_headless run_ppe_auto watch_operator_mobile watch_ntfy_commands watch_ide_build" >nul
  if not errorlevel 1 taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq pythonw.exe" /fo list ^| findstr /i "PID:"') do (
  wmic process where "ProcessId=%%a" get CommandLine 2>nul | findstr /i "Probability-prediction-engine ppe_ntfy_listen ppe_watch_operator ppe_headless run_ppe_auto" >nul
  if not errorlevel 1 taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq cmd.exe" /fo list ^| findstr /i "PID:"') do (
  wmic process where "ProcessId=%%a" get CommandLine 2>nul | findstr /i "Probability-prediction-engine run_ppe PPE auto loop watch_operator watch_ntfy watch_ide_build start_ppe_desktop" >nul
  if not errorlevel 1 taskkill /PID %%a /F >nul 2>&1
)

echo.
echo [fix_desktop_stop_all] DONE.
echo   Daily PC stack stopped. Loop + phone commands belong on the Hyper-V VM only.
if /i "%~1"=="--no-pause" exit /b 0
echo.
echo Press any key to close this window...
pause >nul
exit /b 0
