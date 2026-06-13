# Register Task Scheduler: steward Wed/Sun nudges (separate ntfy topic).

param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [string]$WedTaskName = "PPE steward nudge (Wed)",
    [string]$SunTaskName = "PPE steward nudge (Sun)",
    [string]$WedRunTime = "18:00",
    [string]$SunRunTime = "17:00",
    [switch]$Unregister
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$wedRunner = Join-Path $RepoRoot "steward_nudge_wednesday.cmd"
$sunRunner = Join-Path $RepoRoot "steward_nudge_sunday.cmd"

foreach ($path in @($wedRunner, $sunRunner)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing runner: $path"
    }
}

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
    Unregister-ScheduledTask -TaskName $WedTaskName -Confirm:$false -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $SunTaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Removed scheduled tasks: $WedTaskName, $SunTaskName"
    exit 0
}

Register-StewardTask `
    -Name $WedTaskName `
    -Runner $wedRunner `
    -Day Wednesday `
    -RunTime $WedRunTime `
    -Description "PPE steward: book tester outreach. See docs/SOP/STEWARD_OPERATOR_V1.md"

Register-StewardTask `
    -Name $SunTaskName `
    -Runner $sunRunner `
    -Day Sunday `
    -RunTime $SunRunTime `
    -Description "PPE steward: log session or skip reason. See docs/SOP/STEWARD_OPERATOR_V1.md"

Write-Host "Registered scheduled tasks:"
Write-Host "  $WedTaskName — every Wednesday at $WedRunTime (local)"
Write-Host "  $SunTaskName — every Sunday at $SunRunTime (local)"
Write-Host ""
Write-Host "Prerequisite: PPE_NTFY_STEWARD_TOPIC in ppe_operator_notify.local.cmd"
Write-Host ""
Write-Host "Test now:"
Write-Host "  cmd /c `"$wedRunner`""
Write-Host "  python scripts\ppe_steward_nudge.py --dry-run --slot wednesday"
Write-Host ""
Write-Host "Scoreboard anytime:"
Write-Host "  python scripts\ppe_steward_scoreboard.py"
Write-Host ""
Write-Host "Remove:"
Write-Host "  powershell -File scripts\install_steward_nudge_task.ps1 -RepoRoot `"$RepoRoot`" -Unregister"
