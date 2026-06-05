param(
  [Parameter(Mandatory = $true)]
  [string]$RepoRoot
)

# Popup mode: messagebox (default, reliable) | toast | both
# Disable all: PPE_NOTIFY=0
$popupMode = if ($env:PPE_WEEKLY_DIGEST_POPUP) { $env:PPE_WEEKLY_DIGEST_POPUP.ToLowerInvariant() } else { "messagebox" }

if ($env:PPE_NOTIFY -eq "0" -or $env:PPE_NOTIFY -eq "false") { return 0 }

$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$payloadPath = Join-Path $RepoRoot "artifacts\control_plane\WEEKLY_DIGEST_NOTIFY.json"

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
if ($merges) { $body += "`n`n$merges merge(s) to main.`nOpen: docs\RELEASES\WEEKLY_DIGEST.md" }

function Show-ToastWin10 {
  param([string]$Title, [string]$Message)
  try {
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

    # Shell host AUMID — works without registering a custom app (Win10 1903+).
    $appId = "Microsoft.Windows.Shell.RunDialog"
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

function Show-MessageBox {
  param([string]$Title, [string]$Message)
  try {
    Add-Type -AssemblyName System.Windows.Forms
    [void][System.Windows.Forms.MessageBox]::Show(
      $Message,
      $Title,
      [System.Windows.Forms.MessageBoxButtons]::OK,
      [System.Windows.Forms.MessageBoxIcon]::Information
    )
    return $true
  } catch {
    return $false
  }
}

$shown = $false
if ($popupMode -eq "toast" -or $popupMode -eq "both") {
  if (Show-ToastWin10 -Title $title -Message $body) { $shown = $true }
}
if ($popupMode -eq "messagebox" -or $popupMode -eq "both") {
  if (Show-MessageBox -Title $title -Message $body) { $shown = $true }
}

if (-not $shown) {
  [console]::beep(523, 150) | Out-Null
  [console]::beep(659, 150) | Out-Null
  Write-Host "PPE weekly digest notify fallback:"
  Write-Host $title
  Write-Host $body
}

return 0
