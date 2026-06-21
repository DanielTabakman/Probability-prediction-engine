@echo off
REM Propagate ACTIVE_PRODUCT_DIRECTION.json to steering docs.
cd /d "%~dp0.."
python scripts\sync_active_product_direction.py %*
