# Show whether PPE has an active orchestrator/relay run in-flight.
# Reads artifacts/orchestrator/ACTIVE_RUN.json if present.

param(
  [string]$RepoRoot = ""
)

$ErrorActionPreference = "SilentlyContinue"

if (-not $RepoRoot) {
  $RepoRoot = Split-Path -Parent $PSScriptRoot
}
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$p = Join-Path $RepoRoot "artifacts\orchestrator\ACTIVE_RUN.json"

if (Test-Path -LiteralPath $p) {
  Write-Host "ACTIVE_RUN: present"
  Write-Host ("path=" + $p)
  Get-Content -LiteralPath $p -Raw -Encoding UTF8
  exit 0
}

Write-Host "ACTIVE_RUN: none"
Write-Host ("expected_path=" + $p)
exit 0

