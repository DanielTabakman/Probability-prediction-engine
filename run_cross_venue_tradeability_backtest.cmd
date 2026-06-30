@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
python "%CD%\scripts\run_cross_venue_tradeability_backtest.py" %*
exit /b %ERRORLEVEL%
