@echo off
setlocal

REM Weekly human-readable digest (Monday-morning report).
REM Usage:
REM   weekly_digest.cmd generate
REM   weekly_digest.cmd generate --week 2026-06-02
REM   weekly_digest.cmd backfill --weeks 4

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\ppe_weekly_digest.py" --repo-root "%CD%" %*
exit /b %ERRORLEVEL%
