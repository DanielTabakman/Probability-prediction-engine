# SSH key auth diagnose (run on HOST PC). Prompts for VM password once.

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

Write-Host "=== Host ==="
Write-Host "Key pub:  $env:USERPROFILE\.ssh\id_ppe_vm.pub"
if (Test-Path "$env:USERPROFILE\.ssh\id_ppe_vm.pub") {
    Get-Content "$env:USERPROFILE\.ssh\id_ppe_vm.pub"
} else {
    Write-Host "  MISSING"
}
Write-Host "SSH config: $env:USERPROFILE\.ssh\config"
if (Test-Path "$env:USERPROFILE\.ssh\config") {
    Get-Content "$env:USERPROFILE\.ssh\config" | Select-String -Pattern "ppe-vm|IdentityFile"
}

Write-Host ""
Write-Host "=== VM (enter ppeloop Windows password when prompted) ==="

$remoteScript = @'
$ProgressPreference = "SilentlyContinue"
Write-Output "=== VM user ==="
whoami
Write-Output "=== In Administrators group? ==="
whoami /groups | findstr /i "544"
Write-Output "=== User authorized_keys ==="
$f = Join-Path $env:USERPROFILE ".ssh\authorized_keys"
if (Test-Path $f) { Get-Content $f } else { Write-Output "(missing)" }
Write-Output "=== Admin authorized_keys ==="
$a = "C:\ProgramData\ssh\administrators_authorized_keys"
if (Test-Path $a) { Get-Content $a } else { Write-Output "(missing)" }
Write-Output "=== icacls user keys ==="
if (Test-Path $f) { icacls $f }
Write-Output "=== icacls admin keys ==="
if (Test-Path $a) { icacls $a }
Write-Output "=== sshd ==="
Get-Service sshd | Format-Table -AutoSize
'@

$encoded = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($remoteScript))
ssh ppeloop@desktop-caqll8k powershell.exe -NoProfile -NonInteractive -EncodedCommand $encoded

Write-Host ""
Write-Host "=== BatchMode test from host ==="
ssh -i "$env:USERPROFILE\.ssh\id_ppe_vm" -o IdentitiesOnly=yes -o BatchMode=yes -v ppe-vm "echo SSH_OK" 2>&1 | Select-Object -Last 15
