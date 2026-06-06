param(
  [Parameter(Mandatory = $true)]
  [string]$RepoRoot
)

$ErrorActionPreference = "SilentlyContinue"
if ($env:PPE_NOTIFY -eq "0" -or $env:PPE_NOTIFY -eq "false") { return 0 }
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$p = Join-Path $RepoRoot "artifacts\control_plane\OPERATOR_STATUS_NOTIFY.json"
if (-not (Test-Path -LiteralPath $p)) { return 0 }

$j = Get-Content -LiteralPath $p -Raw -Encoding UTF8 | ConvertFrom-Json
$title = [string]$j.title
$body = [string]$j.body
if (-not $title) { $title = "PPE operator status" }
if (-not $body) { $body = "See artifacts/orchestrator/OPERATOR_STATUS.md" }

function Show-ToastWin10 {
  param([string]$Title, [string]$Message)
  try {
    Add-Type -AssemblyName System.Runtime.InteropServices | Out-Null
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

    $appId = "PPE.Operator"
    $xml = [Windows.Data.Xml.Dom.XmlDocument]::new()
    $toastXml = @"
<toast activationType="foreground">
  <visual>
    <binding template="ToastGeneric">
      <text>$Title</text>
      <text>$Message</text>
    </binding>
  </visual>
</toast>
"@
    $xml.LoadXml($toastXml)
    $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($appId).Show($toast)
    return $true
  } catch {
    return $false
  }
}

if (-not (Show-ToastWin10 -Title $title -Message $body)) {
  [console]::beep(880, 200)
  Write-Host "PPE operator: $title"
  Write-Host $body
}
return 0
