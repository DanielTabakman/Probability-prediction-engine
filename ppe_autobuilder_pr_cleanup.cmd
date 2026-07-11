@echo off
setlocal
set "REPO=%~dp0"
pushd "%REPO%" || exit /b 1
python -m scripts.ppe_autobuilder_pr_cleanup --repo "%REPO%" %*
set "RC=%ERRORLEVEL%"
popd
exit /b %RC%
