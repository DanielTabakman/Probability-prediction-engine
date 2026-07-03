# Register Task Scheduler: periodic operator dispatch (opt-in desktop only).

param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [string]$TaskName = "PPE Operator Dispatch",
    [int]$IntervalMinutes = 15,
    [switch]$Unregister
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$optIn = Join-Path $RepoRoot "ppe_operator_desktop_auto.local.cmd"
$runner = Join-Path $RepoRoot "run_ppe_operator_dispatch_scheduled.cmd"

if (-not $Unregister -and -not (Test-Path -LiteralPath $optIn)) {
    throw "Missing opt-in token: $optIn — run setup_desktop_zero_click_build.cmd first"
}

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

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(2) -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) -RepetitionDuration ([TimeSpan]::MaxValue)

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew

$description = "PPE operator dispatch: run burst direct_action every $IntervalMinutes min when PPE_AUTO_DISPATCH opt-in is set."

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description $description `
    -Force | Out-Null

Write-Host "Registered scheduled task: $TaskName"
Write-Host "  Every: ${IntervalMinutes}m"
Write-Host "  Runs: $runner"
