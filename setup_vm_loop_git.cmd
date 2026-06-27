@echo off
REM VM loop-host one-shot: GitHub CLI auth for ppeloop (run in VM console as ppeloop).
REM After winget install, close and reopen PowerShell OR use full path below.
REM See docs/SOP/HUMAN_STEWARD_BACKLOG.md — vm_loop_host_git_push_credentials

cd /d "%~dp0"
set "GH=C:\Program Files\GitHub CLI\gh.exe"
set "PATH=C:\Program Files\GitHub CLI;%PATH%"

echo === PPE VM loop git publish setup ===
echo.

if not exist "%GH%" (
  echo Installing GitHub CLI...
  winget install GitHub.cli --accept-package-agreements --accept-source-agreements
  echo.
  echo IMPORTANT: Close this window, open a NEW PowerShell, cd to repo, run this script again.
  exit /b 1
)

if not exist "ppe_operator_git.local.cmd" (
  echo Creating ppe_operator_git.local.cmd from example...
  copy /Y ppe_operator_git.local.cmd.example ppe_operator_git.local.cmd
  echo Edit ppe_operator_git.local.cmd if name/email should differ from example defaults.
)

echo.
echo --- gh auth status ---
"%GH%" auth status
if errorlevel 1 (
  echo.
  echo Run browser login ^(device code works on phone too^):
  "%GH%" auth login -h github.com -p https -w
)

echo.
echo --- gh auth setup-git ---
"%GH%" auth setup-git

echo.
echo --- verify ---
"%GH%" auth status
git push origin HEAD --dry-run
echo.
if errorlevel 1 (
  echo Push dry-run failed. Complete gh auth login above, then re-run this script.
  exit /b 1
)
echo Done. Loop closeouts should publish ops/loop-publish-* branches automatically.
