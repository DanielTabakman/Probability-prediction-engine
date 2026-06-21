@echo off
REM Triggered ideas — park until relevant chapter, dismiss when processed.
REM   triggered_ideas.cmd              active ideas
REM   triggered_ideas.cmd add ...      see python scripts/ppe_triggered_ideas.py add --help
REM   triggered_ideas.cmd dismiss <id>   hide idea (--purge to delete)

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

if /i "%~1"=="render" (
  python "%CD%\scripts\ppe_triggered_ideas.py" --repo-root "%CD%" render-md
  exit /b %ERRORLEVEL%
)

if /i "%~1"=="add" (
  shift
  python "%CD%\scripts\ppe_triggered_ideas.py" --repo-root "%CD%" add %*
  exit /b %ERRORLEVEL%
)

if /i "%~1"=="dismiss" (
  if "%~2"=="" (
    echo Usage: triggered_ideas.cmd dismiss ^<id^> [--purge]
    exit /b 1
  )
  if /i "%~3"=="--purge" (
    python "%CD%\scripts\ppe_triggered_ideas.py" --repo-root "%CD%" dismiss "%~2" --purge
  ) else (
    python "%CD%\scripts\ppe_triggered_ideas.py" --repo-root "%CD%" dismiss "%~2" %3 %4 %5
  )
  exit /b %ERRORLEVEL%
)

if /i "%~1"=="check" (
  if "%~2"=="" (
    echo Usage: triggered_ideas.cmd check docs/SOP/PHASE_PLANS/....json
    exit /b 1
  )
  python "%CD%\scripts\ppe_triggered_ideas.py" --repo-root "%CD%" check --plan "%~2"
  exit /b %ERRORLEVEL%
)

python "%CD%\scripts\ppe_triggered_ideas.py" --repo-root "%CD%" status
exit /b %ERRORLEVEL%
