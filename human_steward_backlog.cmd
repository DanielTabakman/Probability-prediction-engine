@echo off
REM Human steward backlog — policy/architecture topics (not auto-loop chapters).
REM   human_steward_backlog.cmd          open items summary
REM   human_steward_backlog.cmd render   refresh HUMAN_STEWARD_BACKLOG.md from JSON

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

if /i "%~1"=="render" (
  python "%CD%\scripts\ppe_human_backlog.py" --repo-root "%CD%" --render-md
  exit /b %ERRORLEVEL%
)

python "%CD%\scripts\ppe_human_backlog.py" --repo-root "%CD%" --status
exit /b %ERRORLEVEL%
