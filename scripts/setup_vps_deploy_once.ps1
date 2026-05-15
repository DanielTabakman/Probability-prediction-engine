<#!
  Easiest one-time setup for GitHub Actions -> VPS deploy.

  Step A (this script): create deploy key on this PC, show public key.
  Step B (you, once): paste public key on VPS (script prints exact commands).
  Step C (this script -SecretsOnly): upload secrets to GitHub via gh.

  From repo root:

    powershell -ExecutionPolicy Bypass -File scripts/setup_vps_deploy_once.ps1

    powershell -ExecutionPolicy Bypass -File scripts/setup_vps_deploy_once.ps1 -SecretsOnly `
      -VpsHost "YOUR.VPS.IP" -VpsUser "root" -RerunDeploy
#>
param(
    [switch] $SecretsOnly,
    [string] $VpsHost = $env:VPS_HOST,
    [string] $VpsUser = $env:VPS_USER,
    [switch] $RerunDeploy
)

$ErrorActionPreference = "Stop"
$KeyStem = Join-Path $env:USERPROFILE ".ssh\ppe_github_deploy"
$KeyPrivate = $KeyStem
$KeyPublic = "$KeyStem.pub"
$repo = "DanielTabakman/Probability-prediction-engine"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$setSecrets = Join-Path $scriptDir "set_github_deploy_secrets.ps1"

function Get-GhExe {
    $cmd = Get-Command gh -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $default = "C:\Program Files\GitHub CLI\gh.exe"
    if (Test-Path $default) { return $default }
    throw "Install GitHub CLI and run: gh auth login"
}

if (-not $SecretsOnly) {
    $sshDir = Split-Path $KeyStem -Parent
    if (-not (Test-Path $sshDir)) {
        New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
    }

    if (-not (Test-Path -LiteralPath $KeyPrivate)) {
        Write-Host "Creating deploy key (no passphrase, for GitHub Actions only)..." -ForegroundColor Cyan
        ssh-keygen -t ed25519 -f $KeyPrivate -N '""' -C "ppe-github-actions-deploy"
        Write-Host "  Private: $KeyPrivate" -ForegroundColor Green
        Write-Host "  Public:  $KeyPublic" -ForegroundColor Green
    }
    else {
        Write-Host "Deploy key already exists: $KeyPrivate" -ForegroundColor Yellow
    }

    $pubLine = (Get-Content -LiteralPath $KeyPublic -Raw).Trim()
    Write-Host ""
    Write-Host "========== STEP B: On the VPS (one login) ==========" -ForegroundColor Cyan
    Write-Host "SSH in as you usually do, then paste these lines on the server:" -ForegroundColor White
    Write-Host ""
    Write-Host "mkdir -p ~/.ssh; chmod 700 ~/.ssh"
    Write-Host "echo '$pubLine' >> ~/.ssh/authorized_keys"
    Write-Host "chmod 600 ~/.ssh/authorized_keys"
    Write-Host ""
    Write-Host "Public key file on this PC: $KeyPublic" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "========== STEP C: Back on this PC ==========" -ForegroundColor Cyan
    Write-Host 'powershell -ExecutionPolicy Bypass -File scripts/setup_vps_deploy_once.ps1 -SecretsOnly -VpsHost "YOUR.IP" -VpsUser "root" -RerunDeploy'
    Write-Host ""
    Write-Host "VpsHost = server IP (Hetzner/DigitalOcean panel). VpsUser = name in ssh USER@host." -ForegroundColor DarkGray
    exit 0
}

if (-not $VpsHost -or -not $VpsUser) {
    Write-Host "SecretsOnly needs -VpsHost and -VpsUser." -ForegroundColor Yellow
    exit 1
}
if (-not (Test-Path -LiteralPath $KeyPrivate)) {
    throw "Run without -SecretsOnly first to create $KeyPrivate"
}

Write-Host "Testing SSH..." -ForegroundColor Cyan
& ssh -i $KeyPrivate -o BatchMode=yes -o StrictHostKeyChecking=accept-new "${VpsUser}@${VpsHost}" "echo deploy-key-ok"
if ($LASTEXITCODE -ne 0) {
    Write-Host "SSH test failed. Complete Step B on the VPS, then run -SecretsOnly again." -ForegroundColor Red
    exit 1
}
Write-Host "SSH test OK." -ForegroundColor Green

& $setSecrets -VpsHost $VpsHost -VpsUser $VpsUser -PrivateKeyPath $KeyPrivate

if ($RerunDeploy) {
    $gh = Get-GhExe
    Write-Host "Triggering Deploy VPS workflow..." -ForegroundColor Cyan
    & $gh workflow run "Deploy VPS" --repo $repo --ref main
    Write-Host "Open Actions tab to watch the run." -ForegroundColor Green
}
