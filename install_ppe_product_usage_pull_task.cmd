@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\scripts\install_ppe_product_usage_pull_task.ps1" -RepoRoot "%CD%" %*
