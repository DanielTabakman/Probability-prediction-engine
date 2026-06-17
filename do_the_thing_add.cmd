@echo off
REM Queue an action for DO THE_THING.cmd
REM Usage: do_the_thing_add.cmd desktop_continue "Human label here"

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if "%~1"=="" (
  echo Usage: do_the_thing_add.cmd ^<action^> ["label"]
  echo Actions: advance desktop_build desktop_continue git_pull vm_advance vm_finish autobuilder:...
  exit /b 1
)
python "%CD%\scripts\ppe_do_the_thing.py" add %1 --label "%~2" --source operator
exit /b %ERRORLEVEL%
