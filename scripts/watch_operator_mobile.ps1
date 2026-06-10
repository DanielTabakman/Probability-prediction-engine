# Poll operator status and send ntfy push when verdict changes or loop dies.
# Stop with Ctrl+C in loop mode. Requires PPE_NTFY_TOPIC (see PPE_MOBILE_OPERATOR_V1.md).

param(
  [string]$RepoRoot = "",
  [int]$IntervalSeconds = 120,
  [switch]$Once
)

$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
  $RepoRoot = Split-Path -Parent $PSScriptRoot
}
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

$localEnv = Join-Path $RepoRoot "ppe_operator_local.cmd"
if (-not (Test-Path -LiteralPath $localEnv)) {
  $localEnv = Join-Path $RepoRoot "ppe_operator_notify.local.cmd"
}
if (Test-Path -LiteralPath $localEnv) {
  # cmd /c alone does not export set vars into this PowerShell session.
  $envLines = cmd /c "`"$localEnv`" && set PPE"
  foreach ($line in $envLines) {
    if ($line -match '^(PPE[^=]+)=(.*)$') {
      Set-Item -Path "env:$($matches[1])" -Value $matches[2]
    }
  }
}

$py = Join-Path $RepoRoot "scripts\ppe_watch_operator_mobile.py"
$pyArgs = @("--repo-root", $RepoRoot)
if ($Once) {
  $pyArgs += "--once"
} else {
  $pyArgs += @("--interval", "$IntervalSeconds")
}

Write-Host "PPE mobile watch - repo: $RepoRoot"
if (-not $Once) {
  Write-Host "Interval: $IntervalSeconds s (Ctrl+C to stop)"
}

& python $py @pyArgs
exit $LASTEXITCODE
