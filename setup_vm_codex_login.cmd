@echo off
setlocal
REM VM Codex login via device code — open https://auth.openai.com/codex/device on THIS PC.

cd /d "%~dp0"
set "VM_HOST=ppeloop@desktop-caqll8k"
set "VM_REPO=C:\Users\ppeloop\Probability-prediction-engine"

echo.
echo ============================================================
echo  SETUP VM CODEX LOGIN  (device code — NOT localhost:1455)
echo ============================================================
echo.
echo If you see "localhost:1455" you ran the WRONG shortcut.
echo Use THIS script only — not plain "codex login".
echo.
echo 1. Wait for link + code below.
echo 2. Open https://auth.openai.com/codex/device on THIS PC.
echo 3. Enter the code. Leave this window open until success.
echo.
ssh %VM_HOST% -- "cd /d %VM_REPO% && codex login --device-auth"
set "RC=%ERRORLEVEL%"
echo.
if %RC%==0 (
  echo Login OK. Run SETUP VM CODEX to verify + restart stack.
) else (
  echo Login failed or cancelled.
)
pause
exit /b %RC%
