<#!
  Set GitHub Actions secrets for Deploy VPS (see .github/workflows/deploy-vps.yml).

  Prerequisites: gh auth login, and a PEM deploy key whose public key is on the VPS.

  Example (PowerShell, from repo root):
    powershell -ExecutionPolicy Bypass -File scripts/set_github_deploy_secrets.ps1 `
      -VpsHost "YOUR.VPS.HOSTNAME" `
      -VpsUser "deployuser" `
      -PrivateKeyPath "$env:USERPROFILE\.ssh\your_deploy_key.pem"

  Or set env vars then run with no params:
    $env:VPS_HOST="..."; $env:VPS_USER="..."; $env:VPS_SSH_PRIVATE_KEY_PATH="C:\path\to\key.pem"
    powershell -ExecutionPolicy Bypass -File scripts/set_github_deploy_secrets.ps1
#>
param(
    [string] $VpsHost = $env:VPS_HOST,
    [string] $VpsUser = $env:VPS_USER,
    [string] $PrivateKeyPath = $env:VPS_SSH_PRIVATE_KEY_PATH,
    [string] $ResearchOfferEmail = $env:PPE_RESEARCH_OFFER_EMAIL
)

$ErrorActionPreference = "Stop"
$repo = "DanielTabakman/Probability-prediction-engine"

$gh = Get-Command gh -ErrorAction SilentlyContinue
if (-not $gh) {
    $ghPath = "C:\Program Files\GitHub CLI\gh.exe"
    if (Test-Path $ghPath) { $ghExe = $ghPath } else { throw "Install GitHub CLI (gh) first." }
} else { $ghExe = $gh.Source }

if (-not $VpsHost -or -not $VpsUser -or -not $PrivateKeyPath) {
    Write-Host "Missing -VpsHost, -VpsUser, or -PrivateKeyPath (or set VPS_HOST, VPS_USER, VPS_SSH_PRIVATE_KEY_PATH)." -ForegroundColor Yellow
    exit 1
}
if (-not (Test-Path -LiteralPath $PrivateKeyPath)) {
    throw "Private key file not found: $PrivateKeyPath"
}

$keyRaw = Get-Content -LiteralPath $PrivateKeyPath -Raw
if ($keyRaw -notmatch "BEGIN .+PRIVATE KEY") {
    Write-Warning "Key file does not look like a PEM private key. Continuing anyway."
}

& $ghExe secret set VPS_HOST --repo $repo --body $VpsHost
& $ghExe secret set VPS_USER --repo $repo --body $VpsUser
$keyRaw | & $ghExe secret set VPS_SSH_PRIVATE_KEY --repo $repo

if ($ResearchOfferEmail) {
    & $ghExe secret set PPE_RESEARCH_OFFER_EMAIL --repo $repo --body $ResearchOfferEmail
    Write-Host "Set PPE_RESEARCH_OFFER_EMAIL on $repo." -ForegroundColor Green
}

Write-Host "Set VPS_HOST, VPS_USER, VPS_SSH_PRIVATE_KEY on $repo. Re-run Deploy VPS in Actions." -ForegroundColor Green
