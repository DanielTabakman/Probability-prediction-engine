@echo off
REM Run once on the VM — puts shortcuts on the Desktop so you never hunt for the path.
setlocal
set "REPO=%~dp0"
set "REPO=%REPO:~0,-1%"
set "DESK=%USERPROFILE%\Desktop"

echo Creating Desktop shortcuts in %DESK%
echo Repo: %REPO%

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$repo='%REPO%'; $desk=[Environment]::GetFolderPath('Desktop'); $s=New-Object -ComObject WScript.Shell; " ^
  "$l=$s.CreateShortcut((Join-Path $desk 'PPE Operator Folder.lnk')); $l.TargetPath=$repo; $l.WorkingDirectory=$repo; $l.Save(); " ^
  "foreach($pair in @{ 'VM STATUS'='VM_STATUS.cmd'; 'VM STOP'='VM_STOP.cmd'; 'VM START'='VM_START.cmd'; 'VM RESTART'='VM_RESTART.cmd'; 'VM UPDATE'='VM_UPDATE.cmd' }) { " ^
  "$l=$s.CreateShortcut((Join-Path $desk ($pair.Key + '.lnk'))); $l.TargetPath=(Join-Path $repo $pair.Value); $l.WorkingDirectory=$repo; $l.Save() }"

echo.
echo Done. Look on your VM Desktop for:
echo   PPE Operator Folder
echo   VM STATUS / VM STOP / VM START / VM RESTART / VM UPDATE
echo.
if /i "%~1"=="--no-pause" exit /b 0
pause
