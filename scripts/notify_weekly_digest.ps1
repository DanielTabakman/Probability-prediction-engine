param(
  [Parameter(Mandatory = $true)]
  [string]$RepoRoot
)

# Popup mode: messagebox (default, reliable) | toast | both
# Disable all: PPE_NOTIFY=0
# Skip open prompt: PPE_WEEKLY_DIGEST_AUTO_OPEN=0 (default asks Yes/No to open file)
$popupMode = if ($env:PPE_WEEKLY_DIGEST_POPUP) { $env:PPE_WEEKLY_DIGEST_POPUP.ToLowerInvariant() } else { "messagebox" }
$autoOpen = -not ($env:PPE_WEEKLY_DIGEST_AUTO_OPEN -eq "0" -or $env:PPE_WEEKLY_DIGEST_AUTO_OPEN -eq "false")

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
if ($merges) { $body += "`n`n$merges merge(s) to main." }
$body += "`n`nFull digest:`n$digestPath"
if ($autoOpen) { $body += "`n`nOpen this file now?" }

function Show-ToastWin10 {
  param([string]$Title, [string]$Message)
  try {
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

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

function Open-DigestFile {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) { return $false }
  $Path = (Resolve-Path -LiteralPath $Path).Path

  # Cursor / VS Code CLIs (preferred for this repo).
  foreach ($cmd in @("cursor", "code")) {
    $exe = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($exe) {
      try {
        Start-Process -FilePath $exe.Source -ArgumentList @($Path)
        return $true
      } catch { }
    }
  }

  # Default file association (.md handler).
  try {
    Invoke-Item -LiteralPath $Path
    return $true
  } catch { }

  # Classic Windows shell open (works when Invoke-Item fails).
  try {
    Start-Process -FilePath "cmd.exe" -ArgumentList @("/c", "start", '""', $Path) -WindowStyle Hidden
    return $true
  } catch { }

  # Last resort: highlight file in Explorer.
  try {
    Start-Process -FilePath "explorer.exe" -ArgumentList @("/select,", $Path)
    return $true
  } catch { }

  return $false
}

function Show-MessageBox {
  param([string]$Title, [string]$Message, [bool]$AskOpen)
  try {
    Add-Type -AssemblyName System.Windows.Forms
    if ($AskOpen) {
      $result = [System.Windows.Forms.MessageBox]::Show(
        $Message,
        $Title,
        [System.Windows.Forms.MessageBoxButtons]::YesNo,
        [System.Windows.Forms.MessageBoxIcon]::Information
      )
      return ($result -eq [System.Windows.Forms.DialogResult]::Yes)
    }
    [void][System.Windows.Forms.MessageBox]::Show(
      $Message,
      $Title,
      [System.Windows.Forms.MessageBoxButtons]::OK,
      [System.Windows.Forms.MessageBoxIcon]::Information
    )
    return $false
  } catch {
    return $false
  }
}

$shown = $false
$openFile = $false
if ($popupMode -eq "toast" -or $popupMode -eq "both") {
  if (Show-ToastWin10 -Title $title -Message $body) { $shown = $true }
}
if ($popupMode -eq "messagebox" -or $popupMode -eq "both") {
  $openFile = Show-MessageBox -Title $title -Message $body -AskOpen:$autoOpen
  $shown = $true
}

if ($openFile) {
  if (-not (Open-DigestFile -Path $digestPath)) {
    Add-Type -AssemblyName System.Windows.Forms
    [void][System.Windows.Forms.MessageBox]::Show(
      "Could not open the digest automatically.`n`nOpen manually:`n$digestPath",
      "PPE weekly digest",
      [System.Windows.Forms.MessageBoxButtons]::OK,
      [System.Windows.Forms.MessageBoxIcon]::Warning
    )
  }
}

if (-not $shown) {
  [console]::beep(523, 150) | Out-Null
  [console]::beep(659, 150) | Out-Null
  Write-Host "PPE weekly digest notify fallback:"
  Write-Host $title
  Write-Host $body
  if ($autoOpen -and (Test-Path -LiteralPath $digestPath)) {
    Write-Host "Open: $digestPath"
  }
}

return 0
