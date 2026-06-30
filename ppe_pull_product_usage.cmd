@echo off
setlocal
cd /d "%~dp0"
python "%CD%\scripts\ppe_product_usage.py" --repo-root "%CD%" --pull-from-docker %*
