@echo off
setlocal

REM Regenerate all IDE_BUILD_STARTER_*.md on disk (slim format).
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
python "%CD%\scripts\regenerate_ide_starters.py" --repo-root "%CD%" %*
exit /b %ERRORLEVEL%
