@echo off
setlocal
REM One-time: reduce desktop IDE_BUILD handoff lag (zero-click watcher + logon task).
REM See docs/SOP/DESKTOP_BUILD_EFFICIENCY_V1.md

cd /d "%~dp0"
if not exist "%CD%\ppe_operator_no_loop.local.cmd" (
  if exist "%CD%\ppe_operator_no_loop.local.cmd.example" (
    copy /Y "%CD%\ppe_operator_no_loop.local.cmd.example" "%CD%\ppe_operator_no_loop.local.cmd" >nul
    echo Created ppe_operator_no_loop.local.cmd from example.
  )
)

call "%CD%\setup_desktop_zero_click_build.cmd"
exit /b %ERRORLEVEL%
