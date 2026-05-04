param(
  [Parameter(Mandatory = $true)]
  [string]$RepoRoot
)

$ErrorActionPreference = "SilentlyContinue"
if ($env:PPE_NOTIFY -eq "0" -or $env:PPE_NOTIFY -eq "false") { return 0 }
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$p = Join-Path $RepoRoot "artifacts\orchestrator\LAST_RUN_REPORT.json"
if (-not (Test-Path -LiteralPath $p)) { return 0 }

$j = Get-Content -LiteralPath $p -Raw -Encoding UTF8 | ConvertFrom-Json
$await = [bool]$j.awaiting_user
$kind = [string]$j.kind
$exit = [string]$j.wrapper_exit_code
$slice = [string]$j.slice_id
$plan = [string]$j.plan_path
$bucket = [string]$j.status_bucket

$title = if ($await) { "PPE: needs attention ($kind exit=$exit)" } else { "PPE: run finished ($kind exit=$exit)" }
$bodyLines = @()
if ($slice) { $bodyLines += "slice: $slice" }
if ($plan) { $bodyLines += "plan: $plan" }
$bodyLines += "bucket: $bucket"
$bodyLines += "open: artifacts/orchestrator/LAST_RUN_REPORT.md"
$body = ($bodyLines -join "`n")

function Show-ToastWin10 {
  param([string]$Title, [string]$Message)
  try {
    Add-Type -AssemblyName System.Runtime.InteropServices | Out-Null
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

    $appId = "PPE.Orchestrator"
    $xml = [Windows.Data.Xml.Dom.XmlDocument]::new()
    $toastXml = @"
<toast activationType="foreground">
  <visual>
    <binding template="ToastGeneric">
      <text>$([System.Security.SecurityElement]::Escape($Title))</text>
      <text>$([System.Security.SecurityElement]::Escape($Message))</text>
    </binding>
  </visual>
</toast>
"@
    $xml.LoadXml($toastXml)
    $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($appId).Show($toast) | Out-Null
    return $true
  } catch {
    return $false
  }
}

if (-not (Show-ToastWin10 -Title $title -Message $body)) {
  # Fallback: at least beep differently.
  if ($await) {
    [console]::beep(880, 180) | Out-Null
    [console]::beep(660, 180) | Out-Null
  } else {
    [console]::beep(660, 120) | Out-Null
  }
}

return 0
