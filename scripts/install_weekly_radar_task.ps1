# Register Task Scheduler: weekly_digest_monday.cmd every Monday 06:00 local.
# Prep runs immediately; report (digest + ntfy) delivers at 08:00 local (wait inside .cmd).

param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [string]$TaskName = "PPE Monday morning",
    [string]$RunTime = "06:00",
    [switch]$Unregister
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$runner = Join-Path $RepoRoot "weekly_digest_monday.cmd"

if (-not (Test-Path -LiteralPath $runner)) {
    throw "Missing runner: $runner"
}

if ($Unregister) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName "PPE weekly radar + digest" -Confirm:$false -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName "PPE weekly digest" -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Removed scheduled task: $TaskName"
    exit 0
}

foreach ($legacy in @("PPE weekly radar + digest", "PPE weekly digest")) {
    Unregister-ScheduledTask -TaskName $legacy -Confirm:$false -ErrorAction SilentlyContinue
}

$action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c `"$runner`"" `
    -WorkingDirectory $RepoRoot

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At $RunTime

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew

$description = "PPE Monday: 06:00 prep (autoclean + easy fixes), 08:00 report (radar + digest + ntfy). See docs/SOP/WORKFLOW_EFFICIENCY_OPERATOR_V1.md"

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description $description `
    -Force | Out-Null

Write-Host "Registered scheduled task: $TaskName"
Write-Host "  Every Monday at: $RunTime (local)"
Write-Host "  Runs: $runner"
Write-Host ""
Write-Host "Test now:"
Write-Host "  cmd /c `"$runner`""
Write-Host ""
Write-Host "Remove:"
Write-Host "  powershell -File scripts\install_weekly_radar_task.ps1 -RepoRoot `"$RepoRoot`" -Unregister"
