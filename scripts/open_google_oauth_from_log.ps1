# If auth is running but browser did not open, run this in a second PowerShell window.
$logOut = Join-Path $env:TEMP 'google-docs-mcp-auth-out.log'
$logErr = Join-Path $env:TEMP 'google-docs-mcp-auth-err.log'
if (-not (Test-Path $logOut) -and -not (Test-Path $logErr)) {
    Write-Error ('No log yet — start auth_google_docs_mcp.ps1 first and wait for output.')
}
function Read-LogFileShared {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return '' }
    $fs = [System.IO.File]::Open(
        $Path,
        [System.IO.FileMode]::Open,
        [System.IO.FileAccess]::Read,
        [System.IO.FileShare]::ReadWrite)
    try {
        $reader = New-Object System.IO.StreamReader($fs)
        return $reader.ReadToEnd()
    } finally {
        $reader.Dispose()
        $fs.Dispose()
    }
}
$raw = (Read-LogFileShared $logOut) + (Read-LogFileShared $logErr)
if ($raw -match '(https://accounts\.google\.com/o/oauth2/v2/auth[^\s\r\n]+)') {
    $url = $Matches[0].Trim()
    Write-Host 'Opening:'
    Write-Host $url
    Start-Process $url
} else {
    Write-Host 'Log contents:'
    Write-Host $raw
    Write-Error 'No Google OAuth URL in log yet. Wait for auth script to print the link, then run this again.'
}
