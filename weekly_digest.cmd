@echo off
setlocal

REM Weekly human-readable digest (Monday-morning report).
REM Usage:
REM   weekly_digest.cmd generate
REM   weekly_digest.cmd generate --week 2026-06-02
REM   weekly_digest.cmd backfill --weeks 4
REM   weekly_digest.cmd notify
REM   weekly_digest_monday.cmd   (generate + notify — for Task Scheduler)

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

if /i "%~1"=="notify" goto notify

python "%CD%\scripts\ppe_weekly_digest.py" --repo-root "%CD%" %*
set "RC=%ERRORLEVEL%"
if %RC% neq 0 exit /b %RC%

if /i "%~1"=="generate" goto notify
if /i "%~1"=="backfill" goto notify
exit /b 0

:notify
python "%CD%\scripts\ppe_weekly_digest.py" --repo-root "%CD%" write-notify-payload
if errorlevel 1 exit /b %ERRORLEVEL%
powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\scripts\notify_weekly_digest.ps1" -RepoRoot "%CD%"
exit /b %ERRORLEVEL%
