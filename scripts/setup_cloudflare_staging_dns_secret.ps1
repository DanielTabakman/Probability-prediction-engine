<#!
  One-time: store Cloudflare API token in GitHub Actions for staging DNS automation.

  Prerequisites: gh auth login

  1) Cloudflare → My Profile → API Tokens → Create Token
     Use template "Edit zone DNS" OR custom token with:
       - Zone → DNS → Edit
       - Zone Resources → Include → Specific zone → marketstructureos.com

  2) From repo root (do NOT paste the token in chat):

     powershell -ExecutionPolicy Bypass -File scripts/setup_cloudflare_staging_dns_secret.ps1

     gh will prompt securely for CLOUDFLARE_API_TOKEN.

  Or non-interactive (PowerShell session only — clear history after):

     $env:CLOUDFLARE_API_TOKEN = 'your-token-here'
     powershell -ExecutionPolicy Bypass -File scripts/setup_cloudflare_staging_dns_secret.ps1 -FromEnv

  3) Re-run Deploy VPS Staging in GitHub Actions (or ask the agent).
#>
param(
    [switch] $FromEnv,
    [string] $CloudflareApiToken = $env:CLOUDFLARE_API_TOKEN,
    [string] $ZoneId = $env:CLOUDFLARE_ZONE_ID
)

$ErrorActionPreference = "Stop"
$repo = "DanielTabakman/Probability-prediction-engine"

$gh = Get-Command gh -ErrorAction SilentlyContinue
if (-not $gh) {
    $ghPath = "C:\Program Files\GitHub CLI\gh.exe"
    if (Test-Path $ghPath) { $ghExe = $ghPath } else { throw "Install GitHub CLI (gh) and run: gh auth login" }
} else { $ghExe = $gh.Source }

Write-Host ""
Write-Host "Cloudflare token setup for staging.marketstructureos.com" -ForegroundColor Cyan
Write-Host "Create token: https://dash.cloudflare.com/profile/api-tokens" -ForegroundColor DarkGray
Write-Host "  Permission: Zone - DNS - Edit" -ForegroundColor DarkGray
Write-Host "  Zone: marketstructureos.com only" -ForegroundColor DarkGray
Write-Host ""

if ($FromEnv -and $CloudflareApiToken) {
    & $ghExe secret set CLOUDFLARE_API_TOKEN --repo $repo --body $CloudflareApiToken
    Write-Host "Set CLOUDFLARE_API_TOKEN on $repo." -ForegroundColor Green
} else {
    Write-Host "Opening secure prompt for CLOUDFLARE_API_TOKEN (input hidden)..." -ForegroundColor Yellow
    & $ghExe secret set CLOUDFLARE_API_TOKEN --repo $repo
    Write-Host "Set CLOUDFLARE_API_TOKEN on $repo." -ForegroundColor Green
}

if ($ZoneId) {
    & $ghExe secret set CLOUDFLARE_ZONE_ID --repo $repo --body $ZoneId
    Write-Host "Set CLOUDFLARE_ZONE_ID on $repo." -ForegroundColor Green
} else {
    Write-Host 'CLOUDFLARE_ZONE_ID optional - script resolves zone by name if omitted.' -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "Next: GitHub Actions -> Deploy VPS Staging -> Run workflow" -ForegroundColor Cyan
Write-Host 'Or: gh workflow run deploy-vps-staging.yml --ref main' -ForegroundColor DarkGray
