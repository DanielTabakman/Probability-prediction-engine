@echo off
setlocal
REM VM loop-host recovery: bootstrap + mark product ready + run relay once.
REM Prefer: vm_bootstrap.cmd --recover  (sync + stack + detached run-local)
REM Usage (on VM):  fix_vm_operator.cmd

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist "%CD%\ppe_operator_loop_host.local.cmd" call "%CD%\ppe_operator_loop_host.local.cmd"
set "PPE_OPERATOR_PROFILE=local"
set "PPE_SKIP_ACP=1"

echo [fix_vm_operator] bootstrap (sync progress, heal artifacts, queue repair)...
python "%CD%\scripts\ppe_vm_bootstrap.py" --repo-root "%CD%"
if errorlevel 1 exit /b %ERRORLEVEL%

echo [fix_vm_operator] mark production wiring product slice ready (idempotent)...
call "%CD%\mark_ide_product_ready.cmd" MSOS-ProdWireV1-Product-Slice002 docs/SOP/PHASE_PLANS/msos_production_wiring_v1_relay.json

echo [fix_vm_operator] run relay once (synchronous)...
call "%CD%\run_ppe_local.cmd"
set "RC=%ERRORLEVEL%"

echo [fix_vm_operator] ensure headless stack...
call "%CD%\run_ppe_headless_stack.cmd" --ensure
exit /b %RC%
