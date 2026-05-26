param(
  [Parameter(Mandatory = $true)]
  [string]$RepoRoot,
  [Parameter(Mandatory = $true)]
  [string]$Reason,
  [string]$SliceId = "",
  [string]$PlanPath = ""
)

$ErrorActionPreference = "SilentlyContinue"
if ($env:PPE_NOTIFY -eq "0" -or $env:PPE_NOTIFY -eq "false") { return 0 }

$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$shortReason = if ($Reason.Length -gt 120) { $Reason.Substring(0, 117) + "..." } else { $Reason }

$title = "PPE: run failed early"
$bodyLines = @("reason: $shortReason")
if ($SliceId) { $bodyLines += "slice: $SliceId" }
if ($PlanPath) { $bodyLines += "plan: $PlanPath" }
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
  [console]::beep(990, 200) | Out-Null
  [console]::beep(740, 200) | Out-Null
  [console]::beep(990, 200) | Out-Null
}

return 0
