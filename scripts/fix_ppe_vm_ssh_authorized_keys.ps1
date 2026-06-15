# Fix VM SSH public-key auth (run on HOST PC). Prompts for VM password once.
# Handles Windows OpenSSH quirk: admin users need ProgramData\ssh\administrators_authorized_keys.

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$pub = Join-Path $env:USERPROFILE ".ssh\id_ppe_vm.pub"
if (-not (Test-Path $pub)) {
    Write-Host "Missing $pub" -ForegroundColor Red
    exit 1
}

$pubLine = (Get-Content -Path $pub -Raw).Trim()
if ($pubLine -match "'") {
    Write-Host "Unexpected quote in public key." -ForegroundColor Red
    exit 1
}

Write-Host "Fixing SSH keys on VM (password = Windows login for user ppeloop on the VM) ..."
Write-Host "Nothing shows while you type the password - that is normal."
Write-Host ""

$remoteScript = @"
`$ProgressPreference = 'SilentlyContinue'
`$pub = '$pubLine'
`$marker = `$pub.Split()[1]

function Write-KeyFile(`$path) {
  `$dir = Split-Path `$path -Parent
  if (`$dir -and -not (Test-Path `$dir)) {
    New-Item -ItemType Directory -Force -Path `$dir | Out-Null
  }
  `$lines = @()
  if (Test-Path `$path) {
    `$lines = Get-Content `$path -ErrorAction SilentlyContinue |
      Where-Object { `$_ -and (`$_ -notmatch '^\s*#') -and (`$_ -notmatch '<') -and (`$_ -notmatch [regex]::Escape(`$marker)) }
  }
  `$lines += `$pub
  Set-Content -Path `$path -Value `$lines -Encoding ascii
}

Write-KeyFile (Join-Path `$env:USERPROFILE '.ssh\authorized_keys')
Write-KeyFile 'C:\ProgramData\ssh\administrators_authorized_keys'

`$userSsh = Join-Path `$env:USERPROFILE '.ssh'
`$userKeys = Join-Path `$userSsh 'authorized_keys'
`$adminKeys = 'C:\ProgramData\ssh\administrators_authorized_keys'

if (Test-Path `$userSsh) {
  icacls `$userSsh /inheritance:r | Out-Null
  icacls `$userSsh /grant "`${env:USERNAME}:(OI)(CI)F" /grant "SYSTEM:(OI)(CI)F" | Out-Null
}
if (Test-Path `$userKeys) {
  icacls `$userKeys /inheritance:r | Out-Null
  icacls `$userKeys /grant "`${env:USERNAME}:F" /grant "SYSTEM:F" | Out-Null
}
if (Test-Path `$adminKeys) {
  icacls `$adminKeys /inheritance:r | Out-Null
  icacls `$adminKeys /grant "Administrators:F" /grant "SYSTEM:F" | Out-Null
}

`$inAdmin = (whoami /groups) -match 'S-1-5-32-544' -and (whoami /groups) -notmatch 'Denied'
Write-Output ('KEYS_OK admin_user=' + `$inAdmin)
"@

$encoded = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($remoteScript))
$raw = ssh ppeloop@desktop-caqll8k powershell.exe -NoProfile -NonInteractive -EncodedCommand $encoded 2>&1
$text = ($raw | Out-String).Trim()
if ($text -match "KEYS_OK") {
    Write-Host $text
} else {
    Write-Host "Remote output:" -ForegroundColor Yellow
    Write-Host $text
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Remote fix failed (wrong password or VM unreachable)." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Testing passwordless SSH ..."
ssh -i "$env:USERPROFILE\.ssh\id_ppe_vm" -o IdentitiesOnly=yes -o BatchMode=yes ppe-vm "echo SSH_OK"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Still failing. Run diagnose:" -ForegroundColor Yellow
    Write-Host "  powershell -ExecutionPolicy Bypass -File scripts\diagnose_ppe_vm_ssh.ps1"
    exit 1
}

Write-Host ""
Write-Host "Success - no password needed from now on."
