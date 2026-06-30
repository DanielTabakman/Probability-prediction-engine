@echo off
setlocal
REM Daily cross-venue pipeline: snapshot + ranked scan report.
REM Backtest is weekly (see weekly_digest_monday.cmd) — needs >=14 snapshot days.
REM Usage: run_cross_venue_daily.cmd [--save-snapshot on scan]

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

call "%~dp0collect_cross_venue_snapshot.cmd"
if errorlevel 1 exit /b %ERRORLEVEL%

call "%~dp0run_cross_venue_scan.cmd" --latest-snapshot %*
if errorlevel 1 (
  echo run_cross_venue_daily: scan FAILED exit=%ERRORLEVEL%
  exit /b %ERRORLEVEL%
)

call "%~dp0run_cross_venue_tradeability.cmd" %*
set "RC=%ERRORLEVEL%"
if errorlevel 1 (
  echo run_cross_venue_daily: tradeability FAILED exit=%RC%
) else (
  echo run_cross_venue_daily: OK
)
exit /b %RC%
