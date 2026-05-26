@echo off
setlocal
REM Push current branch when network allows. No-op if PPE_LOCAL_GIT_ONLY=1. See docs/SOP/AGENT_GIT_SETUP.md §6.
set "REPO_ROOT=%~dp0"
set "REPO_ROOT=%REPO_ROOT:~0,-1%"
set "PYTHONPATH=%REPO_ROOT%"
python "%REPO_ROOT%\scripts\ppe_git_network.py" --repo-root "%REPO_ROOT%"
exit /b %ERRORLEVEL%
