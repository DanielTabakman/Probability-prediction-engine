# Google Docs MCP OAuth - loads repo-root .env.mcp, runs browser auth once.
# Usage: powershell -ExecutionPolicy Bypass -File scripts\auth_google_docs_mcp.ps1
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $repoRoot
$envFile = Join-Path $repoRoot '.env.mcp'
if (-not (Test-Path $envFile)) {
    Write-Error 'Missing .env.mcp in repo root. Copy .env.mcp.example to .env.mcp and fill in credentials.'
}
foreach ($line in Get-Content $envFile) {
    if ($line -match '^\s*GOOGLE_CLIENT_ID=(.+)$') { $env:GOOGLE_CLIENT_ID = $matches[1].Trim() }
    if ($line -match '^\s*GOOGLE_CLIENT_SECRET=(.+)$') { $env:GOOGLE_CLIENT_SECRET = $matches[1].Trim() }
}
if (-not $env:GOOGLE_CLIENT_ID -or -not $env:GOOGLE_CLIENT_SECRET) {
    Write-Error '.env.mcp must set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET (one per line, no quotes).'
}
if ($env:GOOGLE_CLIENT_SECRET -eq 'PASTE_YOUR_SECRET_HERE') {
    Write-Error 'Replace PASTE_YOUR_SECRET_HERE in .env.mcp with your real client secret.'
}
$npxPath = $null
$cmd = Get-Command npx.cmd -ErrorAction SilentlyContinue
if ($cmd) { $npxPath = $cmd.Source }
if (-not $npxPath) {
    $fallback = Join-Path ${env:ProgramFiles} 'nodejs\npx.cmd'
    if (Test-Path $fallback) { $npxPath = $fallback }
}
if (-not $npxPath) {
    Write-Error 'npx.cmd not found. Install Node.js LTS from https://nodejs.org/ then open a new PowerShell window.'
}
$tokenPath = Join-Path $env:USERPROFILE '.config\google-docs-mcp\token.json'
$urlPattern = 'https://accounts\.google\.com/o/oauth2/v2/auth[^\s\r\n]+'
$logOut = Join-Path $env:TEMP 'google-docs-mcp-auth-out.log'
$logErr = Join-Path $env:TEMP 'google-docs-mcp-auth-err.log'
Remove-Item $logOut, $logErr -Force -ErrorAction SilentlyContinue
function Read-LogFileShared {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return '' }
    try {
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
    } catch {
        return ''
    }
}
function Get-AuthLogText {
    return (Read-LogFileShared $logOut) + (Read-LogFileShared $logErr)
}

Write-Host 'Starting OAuth (npm may take 30-60s the first time)...'
Write-Host 'Do not paste any URL into PowerShell. Browser will open when the link is ready.'
Write-Host ''

$proc = Start-Process -FilePath $npxPath `
    -ArgumentList @('-y', '@a-bonus/google-docs-mcp', 'auth') `
    -WorkingDirectory $repoRoot `
    -RedirectStandardOutput $logOut `
    -RedirectStandardError $logErr `
    -NoNewWindow `
    -PassThru

$opened = $false
$lastLen = 0
while (-not $proc.HasExited) {
    $raw = Get-AuthLogText
    if ($raw.Length -gt $lastLen) {
        $chunk = $raw.Substring($lastLen)
        Write-Host $chunk -NoNewline
        $lastLen = $raw.Length
        if (-not $opened -and $raw -match $urlPattern) {
            $url = $Matches[0].Trim()
            Write-Host ''
            Write-Host 'Opening browser...'
            Start-Process $url
            $opened = $true
            Write-Host 'Sign in and click Allow, then wait here until you see Done.'
            Write-Host ''
        }
    }
    Start-Sleep -Milliseconds 400
}

$raw = Get-AuthLogText
if ($raw.Length -gt $lastLen) {
    Write-Host $raw.Substring($lastLen) -NoNewline
}

if (-not $opened -and $raw -match $urlPattern) {
    Start-Process $Matches[0].Trim()
    $opened = $true
    Write-Host 'Opened browser from log. Finish sign-in there.'
}

if ($proc.ExitCode -ne 0 -and -not (Test-Path $tokenPath)) {
    Write-Error ('Auth failed (exit ' + $proc.ExitCode + '). Logs: ' + $logOut + ' and ' + $logErr)
}
if (-not (Test-Path $tokenPath)) {
    Write-Error ('No token file yet: ' + $tokenPath + ' — complete browser sign-in and run again if needed.')
}
Write-Host ''
Write-Host ('Done. Token saved under: ' + $tokenPath)
