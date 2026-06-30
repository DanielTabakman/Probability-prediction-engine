@echo off
setlocal

REM Workflow metrics CLI wrapper.
REM Usage:
REM   workflow_metrics.cmd session start
REM   workflow_metrics.cmd session stop --cognitive-load 3 [--roundtrips N]
REM   workflow_metrics.cmd slice close --slice-id ID --size M --roundtrips 2 [--worker-lane manual]
REM   workflow_metrics.cmd summary [--days 7] [--by-lane] [--include-validation]
REM   workflow_metrics.cmd backfill [--limit 10] [--dry-run]
REM   workflow_metrics.cmd export-csv

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\workflow_metrics_cli.py" --repo-root "%CD%" %*
exit /b %ERRORLEVEL%
