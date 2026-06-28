@echo off
setlocal
REM Desktop -> VM: commit staged docs/SOP and loop-publish (ops/loop-publish-* + PR).
REM Never pushes origin/main directly — avoids SSH credential hangs on protected main.
REM Usage: vm_remote_publish.cmd [commit message]

cd /d "%~dp0"
set "PYTHONPATH=%CD%"
set "VM_HOST=ppeloop@desktop-caqll8k"
set "VM_REPO=C:\Users\ppeloop\Probability-prediction-engine"
set "SSH_OPTS=-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=10 -o ServerAliveCountMax=3"
set "MSG=ops: loop publish control-plane steering"
if not "%~1"=="" set "MSG=%~1"

echo [vm_remote_publish] pull on VM...
ssh %SSH_OPTS% %VM_HOST% "cd /d %VM_REPO% && git pull origin main"
if errorlevel 1 exit /b 1

echo [vm_remote_publish] commit staged SOP + loop publish...
ssh %SSH_OPTS% %VM_HOST% "cd /d %VM_REPO% && set PYTHONPATH=%VM_REPO% && set PPE_GIT_CMD_TIMEOUT=120 && python scripts\ppe_vm_remote_ops.py commit-and-publish --message \"%MSG%\""
set "RC=%ERRORLEVEL%"

echo [vm_remote_publish] VM status:
ssh %SSH_OPTS% %VM_HOST% "cd /d %VM_REPO% && ppe_autobuilder.cmd status --brief"
exit /b %RC%
