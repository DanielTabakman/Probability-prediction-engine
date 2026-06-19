@echo off
setlocal

REM Human work intake — route through queue; never jump the relay pipeline.
REM   ppe_request.cmd reconcile
REM   ppe_request.cmd --chapter-id msos_billing_stripe_v1 --reason "..." [--apply]
REM   ppe_request.cmd human --title "..." --summary "..." [--apply]
REM Canon: docs/SOP/CONTROL_PLANE_OPERATOR_V1.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_local.cmd" call "%CD%\ppe_operator_local.cmd"
set "PPE_OPERATOR_PROFILE=local"

python "%CD%\scripts\ppe_operator_env.py"
if errorlevel 1 exit /b 1

if /I "%~1"=="reconcile" (
  python "%CD%\scripts\ppe_control_plane.py" --repo-root "%CD%" reconcile
  exit /b %ERRORLEVEL%
)

if /I "%~1"=="human" (
  shift
  python "%CD%\scripts\ppe_control_plane.py" --repo-root "%CD%" human %*
  exit /b %ERRORLEVEL%
)

if /I "%~1"=="request" (
  shift
  python "%CD%\scripts\ppe_control_plane.py" --repo-root "%CD%" request %*
  exit /b %ERRORLEVEL%
)

REM Default: chapter request shorthand
python "%CD%\scripts\ppe_control_plane.py" --repo-root "%CD%" request %*
exit /b %ERRORLEVEL%
