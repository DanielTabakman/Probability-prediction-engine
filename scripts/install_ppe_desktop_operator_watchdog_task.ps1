# Register Task Scheduler: hidden watchdog every N minutes (restart loop/watch if closed).

param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [string]$TaskName = "PPE Desktop Operator Watchdog",
    [int]$IntervalMinutes = 15,
    [switch]$Unregister
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$runner = Join-Path $RepoRoot "run_ppe_desktop_operator_watchdog.cmd"
if (-not (Test-Path -LiteralPath $runner)) {
    throw "Missing runner: $runner"
}

if ($IntervalMinutes -lt 5) {
    throw "IntervalMinutes must be >= 5"
}

if ($Unregister) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Removed scheduled task: $TaskName"
    exit 0
}

$action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c `"$runner`"" `
    -WorkingDirectory $RepoRoot

$start = (Get-Date).AddMinutes(1)
$trigger = New-ScheduledTaskTrigger `
    -Once `
    -At $start `
    -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) `
    -RepetitionDuration (New-TimeSpan -Days 3650)

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
    -Hidden

$description = "PPE watchdog: git pull + ensure loop+watch (hidden, every ${IntervalMinutes}m). See docs/SOP/PPE_MOBILE_OPERATOR_V1.md"

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description $description `
    -Force | Out-Null

Write-Host "Registered scheduled task: $TaskName"
Write-Host "  Every: $IntervalMinutes minutes (hidden, no focus steal)"
Write-Host "  Runs: $runner"
Write-Host ""
Write-Host "Test now:"
Write-Host "  cmd /c `"$runner`""
Write-Host ""
Write-Host "Remove:"
Write-Host "  powershell -File scripts\install_ppe_desktop_operator_watchdog_task.ps1 -RepoRoot `"$RepoRoot`" -Unregister"
