@echo off
REM Run from the folder that contains run.bat (double-click or from cmd).
setlocal
cd /d "%~dp0"

echo Project folder: %CD%
echo.

if not exist ".venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Could not create venv. Is Python installed? Try: python --version
        pause
        exit /b 1
    )
)

call .venv\Scripts\activate.bat
echo Installing/updating dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: pip install failed.
    pause
    exit /b 1
)

echo.
echo Starting dashboard... (browser may open automatically)
echo.
streamlit run src/viz/app.py

if errorlevel 1 (
    echo.
    echo Something went wrong. See messages above.
    pause
)
