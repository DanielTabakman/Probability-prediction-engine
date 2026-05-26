@echo off
setlocal
REM Run full phase with local commit/promotion only (no git push). See docs/SOP/AGENT_GIT_SETUP.md §6.
set "PPE_LOCAL_GIT_ONLY=1"
call "%~dp0run_ppe.cmd" %*
exit /b %ERRORLEVEL%
