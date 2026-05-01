param(
  [int]$Keep = 3,
  [switch]$Force
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$wtRoot = Join-Path $repoRoot "_worktrees\\acp_orchestrator"

if (!(Test-Path $wtRoot)) {
  Write-Host "No worktree root found: $wtRoot"
  exit 0
}

$dirs = Get-ChildItem -Path $wtRoot -Directory | Sort-Object LastWriteTime -Descending

if ($dirs.Count -le $Keep) {
  Write-Host "Nothing to prune. Worktrees=$($dirs.Count), Keep=$Keep"
  exit 0
}

$toDelete = $dirs | Select-Object -Skip $Keep

Write-Host "Worktree root: $wtRoot"
Write-Host "Keeping newest $Keep worktrees:"
$dirs | Select-Object -First $Keep | ForEach-Object { Write-Host "  KEEP  $($_.Name)  $($_.LastWriteTime)" }

Write-Host ""
Write-Host "Candidates to delete:"
$toDelete | ForEach-Object { Write-Host "  DEL?  $($_.Name)  $($_.LastWriteTime)" }

if (-not $Force) {
  Write-Host ""
  Write-Host "Dry run only. Re-run with -Force to delete."
  exit 0
}

foreach ($d in $toDelete) {
  Write-Host "Deleting $($d.FullName)"
  Remove-Item -Recurse -Force $d.FullName
}

Write-Host "Done."

