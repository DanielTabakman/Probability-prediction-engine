@echo off
setlocal
REM Research pipeline: all collectors + eligible tests (registry-driven).
REM See docs/SOP/RESEARCH_PIPELINE_V1.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\run_research_daily.py" --write %*
set "RC=%ERRORLEVEL%"
if errorlevel 1 (
  echo run_research_daily: FAILED exit=%RC%
) else (
  echo run_research_daily: OK
)
exit /b %RC%
