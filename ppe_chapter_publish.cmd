@echo off
setlocal
set "REPO=%~dp0"
if "%PPE_CHAPTER_PUBLISH%"=="" set "PPE_CHAPTER_PUBLISH=1"
python "%REPO%scripts\ppe_chapter_publisher.py" --repo "%REPO%" %*
exit /b %ERRORLEVEL%
