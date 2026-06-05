@echo off
setlocal

REM Rolling dev release changelog.
REM Usage:
REM   dev_changelog.cmd refresh
REM   dev_changelog.cmd refresh --day 2026-06-03
REM   dev_changelog.cmd backfill --days 30
REM   dev_changelog.cmd append-event --kind chapter_closed --slice-id ID [--title T] [--phase-plan PATH]

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\ppe_dev_changelog.py" --repo-root "%CD%" %*
exit /b %ERRORLEVEL%
