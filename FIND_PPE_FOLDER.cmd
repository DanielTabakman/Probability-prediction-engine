@echo off
REM Search this PC for the PPE repo if you forgot the path. Double-click anywhere.
echo Searching for Probability-prediction-engine folder...
echo.
for %%d in (C D E F) do (
  if exist "%%d:\Users" (
    for /f "delims=" %%p in ('dir /s /b /ad "%%d:\Users\*\Probability-prediction-engine" 2^>nul') do (
      echo FOUND: %%p
    )
  )
)
echo.
echo Expected on VM: C:\Users\ppeloop\Probability-prediction-engine
echo Expected on desktop: C:\Users\USER\Desktop\Probability-prediction-engine
echo.
pause
