# Register Task Scheduler: steward Mon/Thu nudges (separate ntfy topic).

param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [string]$MonTaskName = "PPE steward nudge (Mon)",
    [string]$ThuTaskName = "PPE steward nudge (Thu)",
    [string]$MonRunTime = "10:00",
    [string]$ThuRunTime = "18:00",
    [switch]$Unregister
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$monRunner = Join-Path $RepoRoot "steward_nudge_monday.cmd"
$thuRunner = Join-Path $RepoRoot "steward_nudge_thursday.cmd"

foreach ($path in @($monRunner, $thuRunner)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing runner: $path"
    }
}

$LegacyTaskNames = @(
    "PPE steward nudge (Wed)",
    "PPE steward nudge (Sun)"
)

function Register-StewardTask {
    param(
        [string]$Name,
        [string]$Runner,
        [System.DayOfWeek]$Day,
        [string]$RunTime,
        [string]$Description
    )
    $action = New-ScheduledTaskAction `
        -Execute "cmd.exe" `
        -Argument "/c `"$Runner`"" `
        -WorkingDirectory $RepoRoot
    $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $Day -At $RunTime
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -MultipleInstances IgnoreNew
    Register-ScheduledTask `
        -TaskName $Name `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description $Description `
        -Force | Out-Null
}

if ($Unregister) {
    Unregister-ScheduledTask -TaskName $MonTaskName -Confirm:$false -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $ThuTaskName -Confirm:$false -ErrorAction SilentlyContinue
    foreach ($legacy in $LegacyTaskNames) {
        Unregister-ScheduledTask -TaskName $legacy -Confirm:$false -ErrorAction SilentlyContinue
    }
    Write-Host "Removed scheduled tasks: $MonTaskName, $ThuTaskName (+ legacy Wed/Sun if present)"
    exit 0
}

foreach ($legacy in $LegacyTaskNames) {
    Unregister-ScheduledTask -TaskName $legacy -Confirm:$false -ErrorAction SilentlyContinue
}

Register-StewardTask `
    -Name $MonTaskName `
    -Runner $monRunner `
    -Day Monday `
    -RunTime $MonRunTime `
    -Description "PPE steward: book tester outreach. See docs/SOP/STEWARD_OPERATOR_V1.md"

Register-StewardTask `
    -Name $ThuTaskName `
    -Runner $thuRunner `
    -Day Thursday `
    -RunTime $ThuRunTime `
    -Description "PPE steward: log session or skip reason. See docs/SOP/STEWARD_OPERATOR_V1.md"

Write-Host "Registered scheduled tasks:"
Write-Host "  $MonTaskName — every Monday at $MonRunTime (local)"
Write-Host "  $ThuTaskName — every Thursday at $ThuRunTime (local)"
Write-Host ""
Write-Host "Prerequisite: PPE_NTFY_STEWARD_TOPIC in ppe_operator_notify.local.cmd"
Write-Host ""
Write-Host "Test now:"
Write-Host "  cmd /c `"$monRunner`""
Write-Host "  python scripts\ppe_steward_nudge.py --dry-run --slot monday"
Write-Host ""
Write-Host "Scoreboard anytime:"
Write-Host "  python scripts\ppe_steward_scoreboard.py"
Write-Host ""
Write-Host "Remove:"
Write-Host "  powershell -File scripts\install_steward_nudge_task.ps1 -RepoRoot `"$RepoRoot`" -Unregister"
