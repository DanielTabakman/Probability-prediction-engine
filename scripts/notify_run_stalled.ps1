param(
  [Parameter(Mandatory = $true)]
  [string]$RepoRoot,
  [Parameter(Mandatory = $true)]
  [ValidateSet("sus", "hard")]
  [string]$Level,
  [string]$SliceId = "",
  [string]$PlanPath = "",
  [int]$ElapsedMinutes = 0,
  [int]$LimitMinutes = 0
)

$ErrorActionPreference = "SilentlyContinue"
if ($env:PPE_NOTIFY -eq "0" -or $env:PPE_NOTIFY -eq "false") { return 0 }

$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

$title = if ($Level -eq "hard") {
  "PPE: run killed (hard timeout)"
} else {
  "PPE: run slow (SUS threshold)"
}

$bodyLines = @()
if ($SliceId) { $bodyLines += "slice: $SliceId" }
if ($PlanPath) { $bodyLines += "plan: $PlanPath" }
if ($ElapsedMinutes -gt 0 -and $LimitMinutes -gt 0) {
  $bodyLines += "elapsed: ${ElapsedMinutes}m (limit ${LimitMinutes}m)"
}
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
  if ($Level -eq "hard") {
    [console]::beep(880, 220) | Out-Null
    [console]::beep(880, 220) | Out-Null
    [console]::beep(660, 220) | Out-Null
  } else {
    [console]::beep(740, 160) | Out-Null
    [console]::beep(740, 160) | Out-Null
  }
}

return 0
