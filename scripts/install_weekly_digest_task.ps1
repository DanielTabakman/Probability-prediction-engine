# Register Task Scheduler: weekly_digest_monday.cmd every Monday morning (local time).

param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [string]$TaskName = "PPE weekly digest",
    [string]$RunTime = "09:00",
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
    Write-Host "Removed scheduled task: $TaskName"
    exit 0
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

$description = "PPE weekly digest: generate summary + ntfy phone push. See docs/SOP/WORKFLOW_EFFICIENCY_OPERATOR_V1.md"

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
Write-Host "  powershell -File scripts\install_weekly_digest_task.ps1 -RepoRoot `"$RepoRoot`" -Unregister"
