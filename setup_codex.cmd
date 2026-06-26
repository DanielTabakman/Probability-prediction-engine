@echo off
setlocal

REM One-time desktop setup for Codex CLI (headless + desktop BUILD worker).
REM See docs/SOP/PPE_NEAR_ZERO_API_OPERATOR_V1.md

cd /d "%~dp0"
set "PYTHONPATH=%CD%"

where codex >nul 2>&1
if %ERRORLEVEL%==0 (
  echo [setup_codex] codex already on PATH
  codex --version
  goto :auth
)

if exist "%LOCALAPPDATA%\Programs\OpenAI\Codex\bin\codex.exe" (
  echo [setup_codex] found standalone install at %LOCALAPPDATA%\Programs\OpenAI\Codex\bin\codex.exe
  "%LOCALAPPDATA%\Programs\OpenAI\Codex\bin\codex.exe" --version
  goto :auth
)

if exist "%APPDATA%\npm\codex.cmd" (
  echo [setup_codex] found %APPDATA%\npm\codex.cmd
  echo Add npm global bin to PATH if codex is not found in new shells.
  goto :auth
)

echo [setup_codex] installing Codex CLI for Windows...
powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://chatgpt.com/codex/install.ps1 | iex"
if errorlevel 1 (
  echo [setup_codex] install failed — try: npm install -g @openai/codex
  echo See https://github.com/openai/codex#quickstart
  exit /b 1
)

:auth
set "CODEX_EXE="
where codex >nul 2>&1
if %ERRORLEVEL%==0 set "CODEX_EXE=codex"
if not defined CODEX_EXE if exist "%LOCALAPPDATA%\Programs\OpenAI\Codex\bin\codex.exe" (
  set "CODEX_EXE=%LOCALAPPDATA%\Programs\OpenAI\Codex\bin\codex.exe"
)
if not defined CODEX_EXE if exist "%APPDATA%\npm\codex.cmd" set "CODEX_EXE=%APPDATA%\npm\codex.cmd"
if not defined CODEX_EXE (
  echo [setup_codex] codex not found — open a new terminal or re-run setup.
  exit /b 1
)

echo.
echo [setup_codex] checking login status...
"%CODEX_EXE%" login status
if errorlevel 1 (
  echo.
  echo [setup_codex] run: codex login
  echo Sign in with ChatGPT or set OPENAI_API_KEY per https://developers.openai.com/codex/auth
  exit /b 1
)

echo [setup_codex] done — run verify_codex.cmd
exit /b 0
