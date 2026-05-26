@echo off
setlocal enabledelayedexpansion

REM Alias: engage the next queued chapter once.
REM Usage (from repo root):
REM   engage_next_chapter.cmd
REM   engage_next_chapter.cmd --dry-run
REM   engage_next_chapter.cmd --max-chapters 3 --continuous

call "%~dp0run_queue_cycle.cmd" --max-chapters 1 %*
exit /b %ERRORLEVEL%

