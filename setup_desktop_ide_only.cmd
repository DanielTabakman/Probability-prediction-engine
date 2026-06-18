@echo off
setlocal
REM Daily PC one-shot: IDE BUILD only — no loop, no logon auto-start.
REM See docs/SOP/PPE_VM_DESKTOP_OPERATOR_HANDOFF.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

echo [setup_desktop_ide_only] step 1 — no-loop guard...
if not exist "%CD%\ppe_operator_no_loop.local.cmd" (
  if exist "%CD%\ppe_operator_no_loop.local.cmd.example" (
    copy /Y "%CD%\ppe_operator_no_loop.local.cmd.example" "%CD%\ppe_operator_no_loop.local.cmd" >nul
    echo   created ppe_operator_no_loop.local.cmd
  ) else (
    echo   WARN: missing ppe_operator_no_loop.local.cmd.example
  )
)

if exist "%CD%\ppe_operator_loop_host.local.cmd" (
  if not exist "%CD%\ppe_operator_loop_host.local.cmd.off-desktop" (
    ren "%CD%\ppe_operator_loop_host.local.cmd" ppe_operator_loop_host.local.cmd.off-desktop
    echo   disabled loop_host token on desktop
  )
)

echo.
echo [setup_desktop_ide_only] step 2 — stop stray stack / desktop auto...
if exist "%CD%\DESKTOP_AUTO_STOP.cmd" call "%CD%\DESKTOP_AUTO_STOP.cmd" 2>nul
if exist "%CD%\fix_desktop_stop_all.cmd" call "%CD%\fix_desktop_stop_all.cmd" --no-pause 2>nul
if exist "%CD%\run_ppe_headless_stack.cmd" call "%CD%\run_ppe_headless_stack.cmd" --stop 2>nul

echo.
echo [setup_desktop_ide_only] step 3 — remove legacy logon tasks (if any)...
schtasks /Delete /TN "PPE Desktop Operator" /F 2>nul
schtasks /Delete /TN "PPE Desktop Operator Watchdog" /F 2>nul
schtasks /Delete /TN "PPE Headless Stack" /F 2>nul

echo.
echo [setup_desktop_ide_only] step 4 — desktop shortcuts...
if exist "%CD%\setup_desktop_shortcuts.cmd" call "%CD%\setup_desktop_shortcuts.cmd"

echo.
echo ============================================================
echo  Desktop is IDE-BUILD-only. Loop runs on the Hyper-V VM.
echo  Zero-click: setup_desktop_zero_click_build.cmd
echo  Buttons: DESKTOP BUILD, DESKTOP CONTINUE, DESKTOP ZERO CLICK START/STOP
echo ============================================================
echo.
pause
exit /b 0
