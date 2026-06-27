@echo off
REM VM loop-host one-shot: GitHub CLI auth for ppeloop (run in VM console as ppeloop, not SSH-only).
REM See docs/SOP/HUMAN_STEWARD_BACKLOG.md — vm_loop_host_git_push_credentials

cd /d "%~dp0"
echo === PPE VM loop git publish setup ===
echo.

where gh >nul 2>&1
if errorlevel 1 (
  echo Installing GitHub CLI...
  winget install GitHub.cli --accept-package-agreements --accept-source-agreements
)

if not exist "ppe_operator_git.local.cmd" (
  echo Copy ppe_operator_git.local.cmd.example -^> ppe_operator_git.local.cmd and set name/email.
  copy /Y ppe_operator_git.local.cmd.example ppe_operator_git.local.cmd
)

echo.
echo 1. gh auth login -h github.com -p https -w
gh auth login -h github.com -p https -w
echo.
echo 2. gh auth setup-git
gh auth setup-git
echo.
echo 3. Verify
gh auth status
git push origin HEAD --dry-run
echo.
echo Done. Closeout should publish ops/loop-publish-* branches automatically.
