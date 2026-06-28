# Register Task Scheduler: daily Options Horizon surface archive collector (VM).
param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [string]$TaskName = "PPE Horizon Surface Collector",
    [string]$RunAt = "06:30",
    [switch]$Unregister
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$runner = Join-Path $RepoRoot "collect_horizon_surface_snapshot.cmd"
if (-not (Test-Path -LiteralPath $runner)) {
    throw "Missing runner: $runner"
}

$logDir = Join-Path $RepoRoot "artifacts\orchestrator"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logFile = Join-Path $logDir "horizon_surface_collector.log"

if ($Unregister) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Removed scheduled task: $TaskName"
    exit 0
}

$action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c `"$runner`" >> `"$logFile`" 2>&1" `
    -WorkingDirectory $RepoRoot

$trigger = New-ScheduledTaskTrigger -Daily -At $RunAt

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Options Horizon: daily Deribit BTC surface snapshot for replay archive." `
    -Force | Out-Null

Write-Host "Registered: $TaskName (daily at $RunAt local)"
Write-Host "  Runs: $runner"
Write-Host "  Log:  $logFile"
