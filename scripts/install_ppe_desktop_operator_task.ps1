# Register Task Scheduler: run_ppe_desktop_operator.cmd at user logon.

param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [string]$TaskName = "PPE Desktop Operator",
    [switch]$Unregister
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$runner = Join-Path $RepoRoot "run_ppe_desktop_operator.cmd"

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

$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew

$description = "PPE local loop: propagate queue, ensure loop+watch, git pull. See docs/SOP/PPE_MOBILE_OPERATOR_V1.md"

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description $description `
    -Force | Out-Null

Write-Host "Registered scheduled task: $TaskName"
Write-Host "  At logon for: $env:USERNAME"
Write-Host "  Runs: $runner"
Write-Host ""
Write-Host "Test now:"
Write-Host "  cmd /c `"$runner`""
Write-Host ""
Write-Host "Remove:"
Write-Host "  powershell -File scripts\install_ppe_desktop_operator_task.ps1 -RepoRoot `"$RepoRoot`" -Unregister"
