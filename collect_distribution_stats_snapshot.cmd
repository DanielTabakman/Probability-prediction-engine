@echo off
setlocal
REM Daily BTC distribution stats snapshot (Deribit implied lab export path).
REM See docs/SOP/RESEARCH_PIPELINE_V1.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\collect_distribution_stats_snapshot.py" %*
set "RC=%ERRORLEVEL%"
if errorlevel 1 (
  echo collect_distribution_stats_snapshot: FAILED exit=%RC%
) else (
  echo collect_distribution_stats_snapshot: OK
)
exit /b %RC%
