# Register Task Scheduler: weekly VM git/worktree hygiene (fix_vm_operator).
param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [string]$TaskName = "PPE VM Hygiene",
    [int]$IntervalDays = 7,
    [switch]$Unregister
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$runner = Join-Path $RepoRoot "VM_HYGIENE.cmd"
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

$start = (Get-Date).Date.AddHours(3)
$trigger = New-ScheduledTaskTrigger -Once -At $start -RepetitionInterval (New-TimeSpan -Days $IntervalDays) -RepetitionDuration (New-TimeSpan -Days 3650)

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
    -Description "PPE VM weekly hygiene: detach worktrees, heal git, ensure stack." `
    -Force | Out-Null

Write-Host "Registered: $TaskName (every ${IntervalDays} day(s))"
Write-Host "  Runs: $runner --quiet"
