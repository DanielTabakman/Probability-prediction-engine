# Register Task Scheduler: desktop VM SSH reachability watchdog (not relay).
param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [string]$TaskName = "PPE Network Watchdog",
    [int]$IntervalMinutes = 15,
    [switch]$Unregister
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$runner = Join-Path $RepoRoot "scripts\ppe_network_watchdog.cmd"
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
    -Description "PPE desktop: SSH probe to ppe-vm; ntfy after 3 consecutive failures (not relay)." `
    -Force | Out-Null

Write-Host "Registered: $TaskName (every ${IntervalMinutes}m)"
Write-Host "  Runs: $runner"
Write-Host "  Alert: after 3 failures (~$($IntervalMinutes * 3)m sustained VM unreachable)"
Write-Host ""
Write-Host "Test now:"
Write-Host "  cmd /c `"$runner`""
Write-Host ""
Write-Host "Remove:"
Write-Host "  powershell -File scripts\install_ppe_network_watchdog_task.ps1 -RepoRoot `"$RepoRoot`" -Unregister"
