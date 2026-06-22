@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"

echo install_operator: PPE operator stack bootstrap
if not exist "ppe_operator_local.cmd" (
  echo   hint: copy ppe_operator_near_zero_api.local.cmd.example to ppe_operator_local.cmd
)

call "%~dp0start_ppe_headless_stack.cmd"
if errorlevel 1 exit /b 1

python "%CD%\scripts\ppe_autobuilder.py" ensure
python "%CD%\scripts\ppe_autobuilder.py" status --brief --write
echo install_operator: done — see docs\SOP\OPERATOR_QUICKSTART_V1.md
exit /b 0
