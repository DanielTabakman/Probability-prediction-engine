@echo off
REM === VM ONLY — double-click to download latest scripts from GitHub ===
REM Use this BEFORE VM_STATUS / VM_START if those files are missing or old.

cd /d "%~dp0"
echo [VM_UPDATE] folder: %CD%
echo.

where git >nul 2>&1
if errorlevel 1 (
  echo ERROR: git is not installed or not on PATH on this VM.
  echo Install Git for Windows, then run this file again.
  goto done
)

echo [VM_UPDATE] pulling latest from GitHub...
git pull origin main
if errorlevel 1 (
  echo.
  echo ERROR: git pull failed. Common fixes:
  echo   - check internet on the VM
  echo   - if it says merge conflict, ask the desktop agent for help
  goto done
)

echo.
echo [VM_UPDATE] ensuring ntfy restart secret...
set "PYTHONPATH=%CD%"
python "%CD%\scripts\ensure_ntfy_cmd_secret.py" --repo-root "%CD%"

echo.
echo [VM_UPDATE] refreshing Desktop shortcuts if needed...
python "%CD%\scripts\ppe_operator_shortcuts.py" --repo-root "%CD%" --apply --quiet

echo.
echo [VM_UPDATE] OK. You should now see these files in this folder:
echo   VM_STOP.cmd   VM_STATUS.cmd   VM_START.cmd   check_vm_loop.cmd
dir /b VM_*.cmd check_vm_loop.cmd 2>nul

:done
echo.
echo Press any key to close...
pause >nul
