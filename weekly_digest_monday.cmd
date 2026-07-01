@echo off
setlocal

REM Monday morning pipeline (single Task Scheduler entry):
REM   1. ~06:00 prep — autoclean + easy autofix
REM   2. wait until 08:00 local
REM   3. workflow radar (friction scan, cleanup already done)
REM   4. weekly digest + phone notify
REM Disable toasts: set PPE_NOTIFY=0

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_local.cmd" call "%CD%\ppe_operator_local.cmd"

call "%~dp0monday_morning_prep.cmd" prep
if errorlevel 1 exit /b %ERRORLEVEL%

call "%~dp0monday_morning_prep.cmd" wait
if errorlevel 1 exit /b %ERRORLEVEL%

if exist "%CD%\ppe_pull_product_usage.cmd" (
  call "%CD%\ppe_pull_product_usage.cmd"
  if errorlevel 1 echo weekly_digest_monday: product usage pull skipped — continuing
)

python "%CD%\scripts\ppe_jsonl_retention.py" --repo-root "%CD%" --apply
if errorlevel 1 echo weekly_digest_monday: jsonl retention skipped — continuing

python "%CD%\scripts\ppe_feedback_steward_hook.py" --repo-root "%CD%"
if errorlevel 1 echo weekly_digest_monday: feedback steward hook skipped — continuing

call "%~dp0token_audit.cmd" --prune-stale
if errorlevel 1 exit /b %ERRORLEVEL%

call "%~dp0run_cross_venue_backtest.cmd"
if errorlevel 1 echo weekly_digest_monday: cross-venue backtest failed — continuing

python "%CD%\scripts\ppe_workflow_radar.py" --repo-root "%CD%" generate --no-cleanup
if errorlevel 1 exit /b %ERRORLEVEL%

call "%~dp0ppe_tracking_rollup.cmd" --brief
if errorlevel 1 echo weekly_digest_monday: tracking rollup skipped — continuing

call "%~dp0weekly_digest.cmd" generate
if errorlevel 1 exit /b %ERRORLEVEL%

call "%~dp0weekly_digest.cmd" notify
exit /b %ERRORLEVEL%
