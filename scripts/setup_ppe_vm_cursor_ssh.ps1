# One-time: install SSH key on PPE loop VM for passwordless Cursor Remote-SSH.
# Run from host PowerShell (repo root):
#   cd C:\Users\USER\Desktop\Probability-prediction-engine
#   powershell -ExecutionPolicy Bypass -File scripts\setup_ppe_vm_cursor_ssh.ps1

$ErrorActionPreference = "Stop"
$sshDir = Join-Path $env:USERPROFILE ".ssh"
$key = Join-Path $sshDir "id_ppe_vm"
$pub = "$key.pub"
$config = Join-Path $sshDir "config"
$remoteHost = "ppeloop@desktop-caqll8k"
$remoteTmp = "C:/Users/ppeloop/ppe_vm_key_install.pub"

if (-not (Test-Path $sshDir)) {
    New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
}

if (-not (Test-Path $key)) {
    Write-Host "Generating SSH key at $key ..."
    ssh-keygen -t ed25519 -f $key -N '""' -C "ppe-vm-cursor"
}

$configBody = @"
Host ppe-vm
    HostName desktop-caqll8k
    User ppeloop
    IdentityFile ~/.ssh/id_ppe_vm
    IdentitiesOnly yes
    StrictHostKeyChecking accept-new

Host desktop-caqll8k
    HostName desktop-caqll8k
    User ppeloop
    IdentityFile ~/.ssh/id_ppe_vm
    IdentitiesOnly yes
    StrictHostKeyChecking accept-new

"@
if (-not (Test-Path $config) -or -not (Select-String -Path $config -Pattern "Host ppe-vm" -Quiet)) {
    Add-Content -Path $config -Value $configBody
    Write-Host "Updated $config"
}

Write-Host ""
Write-Host "Step 1/2: copy public key to VM (enter VM password when prompted) ..."
scp $pub "${remoteHost}:${remoteTmp}"
if ($LASTEXITCODE -ne 0) {
    Write-Host "scp failed." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Step 2/2: install key in authorized_keys (enter VM password again if prompted) ..."
ssh $remoteHost 'mkdir C:\Users\ppeloop\.ssh 2>nul & type C:\Users\ppeloop\ppe_vm_key_install.pub >> C:\Users\ppeloop\.ssh\authorized_keys & del C:\Users\ppeloop\ppe_vm_key_install.pub'
if ($LASTEXITCODE -ne 0) {
    Write-Host "ssh install failed." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Testing passwordless SSH ..."
ssh -o BatchMode=yes ppe-vm "echo SSH_OK"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Passwordless login failed." -ForegroundColor Yellow
    Write-Host "On VM (Hyper-V console), run as Administrator if needed:"
    Write-Host "  icacls C:\Users\ppeloop\.ssh /inheritance:r /grant ppeloop:F"
    Write-Host "  icacls C:\Users\ppeloop\.ssh\authorized_keys /inheritance:r /grant ppeloop:F"
    exit 1
}

ssh -o BatchMode=yes ppe-vm "cd /d C:\Users\ppeloop\Probability-prediction-engine && ppe_autobuilder.cmd status --brief"
Write-Host ""
Write-Host "=== Cursor Remote-SSH (one time in Cursor UI) ==="
Write-Host "1. Extensions -> install Remote - SSH (Microsoft)"
Write-Host "2. Ctrl+Shift+P -> Remote-SSH: Connect to Host -> ppe-vm"
Write-Host "3. File -> Open Folder -> C:\Users\ppeloop\Probability-prediction-engine"
Write-Host "4. Bottom-left should show SSH: ppe-vm"
Write-Host ""
Write-Host "Daily coding stays on THIS machine. Only open ppe-vm for VM operator fixes."
