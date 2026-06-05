param(
  [Parameter(Mandatory = $true)]
  [string]$RepoRoot
)

$ErrorActionPreference = "SilentlyContinue"
if ($env:PPE_NOTIFY -eq "0" -or $env:PPE_NOTIFY -eq "false") { return 0 }

$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$payloadPath = Join-Path $RepoRoot "artifacts\control_plane\WEEKLY_DIGEST_NOTIFY.json"
$digestPath = Join-Path $RepoRoot "docs\RELEASES\WEEKLY_DIGEST.md"

if (-not (Test-Path -LiteralPath $payloadPath)) {
  $py = Join-Path $RepoRoot "scripts\ppe_weekly_digest.py"
  if (Test-Path -LiteralPath $py) {
    $env:PYTHONPATH = $RepoRoot
    & python $py --repo-root $RepoRoot write-notify-payload | Out-Null
  }
}

if (-not (Test-Path -LiteralPath $payloadPath)) { return 1 }

$j = Get-Content -LiteralPath $payloadPath -Raw -Encoding UTF8 | ConvertFrom-Json
$week = [string]$j.week_monday
$inShort = [string]$j.in_short
$merges = [string]$j.merge_count

$title = "PPE weekly digest (week of $week)"
$body = $inShort
if ($merges) { $body += "`n$merges merge(s) to main - open docs/RELEASES/WEEKLY_DIGEST.md" }

function Show-ToastWin10 {
  param([string]$Title, [string]$Message)
  try {
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

    $appId = "PPE.WeeklyDigest"
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
  [console]::beep(523, 150) | Out-Null
  [console]::beep(659, 150) | Out-Null
  Write-Host $title
  Write-Host $body
}

return 0
