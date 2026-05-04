# Live progress dashboard while orchestrator/relay slices run.
# Polls logbook, newest ACP worktree, relay current_job, and newest relay events.log.
# Stop with Ctrl+C.

param(
  [string]$RepoRoot = "",
  [int]$IntervalSeconds = 3,
  [int]$LogbookTail = 15,
  [int]$RelayEventsTail = 30
)

$ErrorActionPreference = "SilentlyContinue"

if (-not $RepoRoot) {
  $RepoRoot = Split-Path -Parent $PSScriptRoot
}
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

$wtRoot = Join-Path $RepoRoot "_worktrees\acp_orchestrator"
$logPath = Join-Path $RepoRoot "artifacts\logbook\ppe_events.jsonl"

function Get-NewestWorktreeDir {
  if (-not (Test-Path -LiteralPath $wtRoot)) { return $null }
  Get-ChildItem -LiteralPath $wtRoot -Directory -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
}

function Get-RelayEventsLogs {
  if (-not (Test-Path -LiteralPath $wtRoot)) { return @() }
  Get-ChildItem -LiteralPath $wtRoot -Recurse -Filter "events.log" -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -match '[\\/]artifacts[\\/]relay[\\/]runs[\\/]' }
}

function Read-CurrentJob([string]$worktreePath) {
  if (-not $worktreePath) { return $null }
  $p = Join-Path $worktreePath "artifacts\relay\state\current_job.json"
  if (-not (Test-Path -LiteralPath $p)) { return $null }
  try {
    return (Get-Content -LiteralPath $p -Raw -Encoding UTF8 | ConvertFrom-Json)
  } catch {
    return $null
  }
}

Write-Host "PPE live dashboard — repo: $RepoRoot"
Write-Host "Interval: ${IntervalSeconds}s | Ctrl+C to stop"
Write-Host ""

while ($true) {
  $tick = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
  Write-Host "========== $tick =========="

  $latestWt = Get-NewestWorktreeDir
  if ($latestWt) {
    Write-Host "--- newest worktree ---"
    Write-Host ("path=" + $latestWt.FullName)
    Write-Host ("lastWrite_utc=" + $latestWt.LastWriteTimeUtc.ToString("s") + "Z")
    $job = Read-CurrentJob $latestWt.FullName
    if ($job) {
      Write-Host ("slice_id=" + $job.slice_id)
      Write-Host ("run_id=" + $job.run_id)
      Write-Host ("build_branch=" + $job.build_branch)
    } else {
      Write-Host "current_job.json: (none or unreadable)"
    }
  } else {
    Write-Host "--- newest worktree --- (none under _worktrees\acp_orchestrator)"
  }

  Write-Host "--- logbook (tail $LogbookTail) ---"
  if (Test-Path -LiteralPath $logPath) {
    Get-Content -LiteralPath $logPath -Tail $LogbookTail -Encoding UTF8
  } else {
    Write-Host "(no file yet: artifacts\logbook\ppe_events.jsonl)"
  }

  $relayLogs = Get-RelayEventsLogs
  $newestRelay = $relayLogs | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  Write-Host "--- relay events.log (newest file, tail $RelayEventsTail) ---"
  if ($newestRelay) {
    Write-Host ("file=" + $newestRelay.FullName)
    Write-Host ("lastWrite_utc=" + $newestRelay.LastWriteTimeUtc.ToString("s") + "Z")
    Get-Content -LiteralPath $newestRelay.FullName -Tail $RelayEventsTail -Encoding UTF8
  } else {
    Write-Host "(no events.log under worktrees yet)"
  }

  Write-Host ""
  Start-Sleep -Seconds $IntervalSeconds
}
