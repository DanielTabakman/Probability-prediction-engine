@echo off
setlocal
REM One-time / periodic desktop loop-host bootstrap. See docs/SOP/DESKTOP_OPERATOR_SETUP_STARTER.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

echo === PPE desktop operator bootstrap ===
echo.

if not exist "ppe_operator_notify.local.cmd" (
  echo [ ] ntfy: copy ppe_operator_notify.local.cmd.example -^> ppe_operator_notify.local.cmd
) else (
  echo [x] ntfy: ppe_operator_notify.local.cmd present
)

if not exist "ppe_operator_git.local.cmd" (
  echo [ ] git: copy ppe_operator_git.local.cmd.example -^> ppe_operator_git.local.cmd
) else (
  echo [x] git: ppe_operator_git.local.cmd present
)

call "%CD%\ppe_operator_local.cmd"

python "%CD%\scripts\desktop_operator_preflight.py" --repo-root "%CD%"
set "PF=%ERRORLEVEL%"

echo.
echo --- GitHub CLI (push / PR recovery) ---
gh auth status 2>nul
if errorlevel 1 (
  echo gh not logged in. Run once on this desktop ^(browser opens^):
  echo   gh auth login -h github.com -p https -w
  echo Or from phone SSH: same command; open the URL on any device.
)

echo.
echo --- Git sync (loop) ---
python "%CD%\scripts\ppe_operator_git_sync.py" --repo-root "%CD%" --pull
echo.

echo --- Start stack ---
echo   start_ppe_desktop_operator.cmd
echo.
echo --- Phone triage ---
echo   ssh USER@desktop-ge39o15
echo   run_ppe_operator.cmd --brief
echo.

exit /b %PF%
