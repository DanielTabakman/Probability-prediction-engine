@echo off
REM Product vapor registry — auto-populate / depopulate + dashboard sync
python scripts/ppe_vapor_registry.py --sync %*
