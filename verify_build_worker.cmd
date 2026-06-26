@echo off
setlocal

REM Verify BUILD worker policy: Cursor CLI first, Codex fallback.
REM See docs/SOP/PPE_NEAR_ZERO_API_OPERATOR_V1.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
set "PPE_OPERATOR_PROFILE=local"

python "%CD%\scripts\desktop_operator_preflight.py" --repo-root "%CD%" --cursor-first
exit /b %ERRORLEVEL%
