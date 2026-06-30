@echo off
setlocal
REM Cross-venue tradeability after spread proxy (latest snapshot).
REM See docs/SOP/RESEARCH_PIPELINE_V1.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\run_cross_venue_tradeability.py" --latest-snapshot %*
set "RC=%ERRORLEVEL%"
if errorlevel 1 (
  echo run_cross_venue_tradeability: FAILED exit=%RC%
) else (
  echo run_cross_venue_tradeability: OK
)
exit /b %RC%
