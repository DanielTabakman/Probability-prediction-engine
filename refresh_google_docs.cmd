@echo off
REM Canonical operator command: refresh Google Docs (GOOGLE_DOCS_REFRESH).
REM Usage:
REM   refresh_google_docs.cmd
REM   refresh_google_docs.cmd --dry-run
REM   refresh_google_docs.cmd --trigger cycle-start

set "REPO_ROOT=%~dp0"
set "REPO_ROOT=%REPO_ROOT:~0,-1%"
set "PYTHONPATH=%REPO_ROOT%"

python "%REPO_ROOT%\scripts\google_docs_refresh.py" --repo-root "%REPO_ROOT%" --trigger manual %*
exit /b %ERRORLEVEL%
