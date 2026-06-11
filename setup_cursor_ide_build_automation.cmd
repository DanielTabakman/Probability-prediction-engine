@echo off
setlocal

REM One-time: Cursor Automation setup for IDE BUILD (JSON trigger — not .md).
REM See docs/SOP/CURSOR_IDE_BUILD_AUTOMATION_V1.md
cd /d "%~dp0"
set "PYTHONPATH=%CD%"

python "%CD%\scripts\ppe_cursor_ide_automation_setup.py" --repo-root "%CD%" --open-browser
if errorlevel 1 exit /b 1

echo.
echo [setup_cursor_ide_build_automation] Trigger: .cursor\IDE_BUILD_TRIGGER.json
echo [setup_cursor_ide_build_automation] Alternate: artifacts\orchestrator\IDE_HANDOFF_STATE.json
echo [setup_cursor_ide_build_automation] Prompt: .cursor\IDE_BUILD_AUTOMATION_PROMPT.md
exit /b 0
