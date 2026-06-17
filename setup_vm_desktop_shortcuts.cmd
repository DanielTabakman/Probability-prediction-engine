@echo off
REM Delegates to setup_operator_shortcuts.cmd (auto-detects VM vs desktop).
call "%~dp0setup_operator_shortcuts.cmd" %*
