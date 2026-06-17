@echo off
REM One-time: put DESKTOP_BUILD + DESKTOP_CONTINUE shortcuts on daily PC Desktop.

setlocal
set "REPO=%~dp0"
set "REPO=%REPO:~0,-1%"
set "DESK=%USERPROFILE%\Desktop"

echo Creating Desktop shortcuts in %DESK%

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$repo='%REPO%'; $desk=[Environment]::GetFolderPath('Desktop'); $s=New-Object -ComObject WScript.Shell; " ^
  "$l=$s.CreateShortcut((Join-Path $desk 'PPE Repo (Desktop).lnk')); $l.TargetPath=$repo; $l.WorkingDirectory=$repo; $l.Save(); " ^
  "foreach($pair in @{ 'DESKTOP BUILD'='DESKTOP_BUILD.cmd'; 'DESKTOP CONTINUE'='DESKTOP_CONTINUE.cmd'; 'DESKTOP STOP'='DESKTOP_STOP.cmd' }) { " ^
  "$l=$s.CreateShortcut((Join-Path $desk ($pair.Key + '.lnk'))); $l.TargetPath=(Join-Path $repo $pair.Value); $l.WorkingDirectory=$repo; $l.Save() }"

echo.
echo Done. Desktop shortcuts:
echo   DESKTOP BUILD    — open Cursor + start IDE BUILD
echo   DESKTOP CONTINUE — after merge, advance VM relay
echo   DESKTOP STOP     — stop popups on this PC
echo.
if /i "%~1"=="--no-pause" exit /b 0
pause
