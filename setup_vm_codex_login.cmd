@echo off
setlocal
REM VM Codex login via device code (open link on THIS PC, not VM browser).

cd /d "%~dp0"
set "VM_HOST=ppeloop@desktop-caqll8k"
set "VM_REPO=C:\Users\ppeloop\Probability-prediction-engine"

echo.
echo === Codex VM login (device code) ===
echo 1. This window will show a link + code.
echo 2. Open the link in YOUR browser on this daily PC.
echo 3. Enter the code. Wait for success here before closing.
echo.
ssh -t %VM_HOST% "cd /d %VM_REPO% && codex login --device-auth"
set "RC=%ERRORLEVEL%"
echo.
if %RC%==0 (
  echo Login OK. Run setup_vm_codex.cmd again to verify + restart stack.
) else (
  echo Login failed or cancelled.
)
pause
exit /b %RC%
