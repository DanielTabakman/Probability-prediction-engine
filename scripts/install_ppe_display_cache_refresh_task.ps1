# Register Task Scheduler: display cache warm loop (VM / VPS with repo checkout).
param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [string]$TaskName = "PPE Display Cache Refresh",
    [int]$IntervalMinutes = 2,
    [string]$BaseUrl = "http://127.0.0.1:8765",
    [switch]$Unregister
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$runner = Join-Path $RepoRoot "run_display_cache_refresh.cmd"
if (-not (Test-Path -LiteralPath $runner)) {
    throw "Missing runner: $runner"
}

$logDir = Join-Path $RepoRoot "artifacts\orchestrator"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logFile = Join-Path $logDir "display_cache_refresh.log"

if ($Unregister) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Removed scheduled task: $TaskName"
    exit 0
}

$action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c set PPE_DISPLAY_API_BASE_URL=$BaseUrl&& `"$runner`" >> `"$logFile`" 2>&1" `
    -WorkingDirectory $RepoRoot

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) `
    -RepetitionDuration ([TimeSpan]::MaxValue)

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
    -Description "Warm ppe_display_api cache for all enabled assets (interval < TTL)." `
    -Force | Out-Null

Write-Host "Registered: $TaskName (every $IntervalMinutes min)"
Write-Host "  Runs: $runner"
Write-Host "  Base: $BaseUrl"
Write-Host "  Log:  $logFile"
