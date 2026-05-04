# Stream new lines from artifacts/logbook/ppe_events.jsonl (like tail -f).

param(
  [string]$RepoRoot = "",
  [int]$Tail = 40
)

$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
  $RepoRoot = Split-Path -Parent $PSScriptRoot
}
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$logPath = Join-Path $RepoRoot "artifacts\logbook\ppe_events.jsonl"

Write-Host "Tailing logbook (Ctrl+C to stop): $logPath"

if (-not (Test-Path -LiteralPath $logPath)) {
  Write-Host "Waiting for file to appear..."
  while (-not (Test-Path -LiteralPath $logPath)) {
    Start-Sleep -Seconds 1
  }
}

Get-Content -LiteralPath $logPath -Wait -Tail $Tail -Encoding UTF8
