# Register Task Scheduler: VM watchdog (rate-limited stack recovery).
param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [string]$TaskName = "PPE VM Watchdog",
    [int]$IntervalMinutes = 10,
    [switch]$Unregister
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$runner = Join-Path $RepoRoot "VM_WATCHDOG.cmd"
if (-not (Test-Path -LiteralPath $runner)) {
    throw "Missing runner: $runner"
}

if ($Unregister) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Removed scheduled task: $TaskName"
    exit 0
}

$action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c `"$runner`" --quiet" `
    -WorkingDirectory $RepoRoot

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) -RepetitionDuration (New-TimeSpan -Days 3650)

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
    -Description "PPE VM watchdog: restart headless stack when loop down (rate-limited)." `
    -Force | Out-Null

Write-Host "Registered: $TaskName (every ${IntervalMinutes}m)"
Write-Host "  Runs: $runner --quiet"
