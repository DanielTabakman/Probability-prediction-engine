@echo off
REM Load all gitignored operator local env files (repo root = %~dp0).
if exist "%~dp0ppe_operator_local.cmd" call "%~dp0ppe_operator_local.cmd"
if exist "%~dp0ppe_operator_loop_host.local.cmd" call "%~dp0ppe_operator_loop_host.local.cmd"
REM Daily-driver guard only when this machine is NOT the chartered loop host.
if not defined PPE_LOOP_HOST (
  if exist "%~dp0ppe_operator_no_loop.local.cmd" call "%~dp0ppe_operator_no_loop.local.cmd"
)
