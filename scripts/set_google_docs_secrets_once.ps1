$ErrorActionPreference = "Stop"

function Get-EnvFileMap([string]$path) {
  if (!(Test-Path -LiteralPath $path)) { throw "env file not found: $path" }
  $kv = @{}
  foreach ($line in (Get-Content -LiteralPath $path)) {
    $raw = $line
    if ($null -eq $raw) { $raw = "" }
    $s = $raw.Trim()
    if ([string]::IsNullOrWhiteSpace($s)) { continue }
    if ($s.StartsWith("#")) { continue }
    if ($s -match "^([^=]+)=(.*)$") {
      $k = $Matches[1].Trim()
      $v = $Matches[2]
      if ($v.StartsWith('"') -and $v.EndsWith('"')) { $v = $v.Substring(1, $v.Length - 2) }
      $kv[$k] = $v
    }
  }
  return $kv
}

function Require([string]$name, $value) {
  if ([string]::IsNullOrWhiteSpace([string]$value)) { throw "Missing required value: $name" }
  return [string]$value
}

function Set-Secret([string]$repo, [string]$name, [string]$value) {
  Require $name $value | Out-Null
  gh secret set $name --repo $repo -b $value | Out-Null
}

function Get-McpRefreshToken() {
  $tokenPath = Join-Path $env:USERPROFILE ".config\google-docs-mcp\token.json"
  if (!(Test-Path -LiteralPath $tokenPath)) { return $null }
  try {
    $obj = Get-Content -LiteralPath $tokenPath -Raw | ConvertFrom-Json
    return [string]$obj.refresh_token
  } catch {
    return $null
  }
}

$repo = "DanielTabakman/Probability-prediction-engine"
$m = Get-EnvFileMap ".env.mcp"

# Doc IDs (prefer local .env.mcp values)
$masterDocId = $m["PPE_MASTER_DOC_ID"]
$mirrorDocId = $m["MSOS_REPO_TRUTH_DOC_ID"]
if ([string]::IsNullOrWhiteSpace($mirrorDocId)) { $mirrorDocId = $m["PPE_MSOS_MIRROR_DOC_ID"] }

Set-Secret $repo "PPE_MASTER_DOC_ID" (Require "PPE_MASTER_DOC_ID" $masterDocId)
Set-Secret $repo "PPE_MSOS_MIRROR_DOC_ID" (Require "MSOS_REPO_TRUTH_DOC_ID (mirror doc id)" $mirrorDocId)

# OAuth credentials (from .env.mcp)
# OAuth credentials (map from existing .env.mcp names)
$clientId = $m["GOOGLE_OAUTH_CLIENT_ID"]
if ([string]::IsNullOrWhiteSpace($clientId)) { $clientId = $m["GOOGLE_CLIENT_ID"] }
$clientSecret = $m["GOOGLE_OAUTH_CLIENT_SECRET"]
if ([string]::IsNullOrWhiteSpace($clientSecret)) { $clientSecret = $m["GOOGLE_CLIENT_SECRET"] }
$refreshToken = $m["GOOGLE_OAUTH_REFRESH_TOKEN"]
if ([string]::IsNullOrWhiteSpace($refreshToken)) { $refreshToken = $m["GOOGLE_REFRESH_TOKEN"] }
if ([string]::IsNullOrWhiteSpace($refreshToken)) { $refreshToken = Get-McpRefreshToken }

Set-Secret $repo "GOOGLE_OAUTH_CLIENT_ID" (Require "GOOGLE_CLIENT_ID / GOOGLE_OAUTH_CLIENT_ID" $clientId)
Set-Secret $repo "GOOGLE_OAUTH_CLIENT_SECRET" (Require "GOOGLE_CLIENT_SECRET / GOOGLE_OAUTH_CLIENT_SECRET" $clientSecret)

if ([string]::IsNullOrWhiteSpace($refreshToken)) {
  Write-Host ""
  Write-Host "NOTE: No refresh token found."
  Write-Host "Run once (browser opens): npx -y @a-bonus/google-docs-mcp auth"
  Write-Host "Then re-run this script."
  Write-Host "Skipping GOOGLE_OAUTH_REFRESH_TOKEN for now."
} else {
  Set-Secret $repo "GOOGLE_OAUTH_REFRESH_TOKEN" $refreshToken
  Write-Host "OK: GOOGLE_OAUTH_REFRESH_TOKEN set (from MCP token store or .env.mcp)"
}

Write-Host "OK: GitHub secrets set for $repo"

