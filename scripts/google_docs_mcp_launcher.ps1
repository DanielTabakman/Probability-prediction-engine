# MCP stdio entrypoint for Cursor (loads .env.mcp, runs google-docs-mcp).
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$envFile = Join-Path $repoRoot '.env.mcp'
if (Test-Path $envFile) {
    foreach ($line in Get-Content $envFile) {
        if ($line -match '^\s*GOOGLE_CLIENT_ID=(.+)$') { $env:GOOGLE_CLIENT_ID = $matches[1].Trim() }
        if ($line -match '^\s*GOOGLE_CLIENT_SECRET=(.+)$') { $env:GOOGLE_CLIENT_SECRET = $matches[1].Trim() }
    }
}
$env:PATH = (Join-Path ${env:ProgramFiles} 'nodejs') + ';' + $env:PATH
Set-Location $repoRoot
$npxPath = Join-Path ${env:ProgramFiles} 'nodejs\npx.cmd'
if (-not (Test-Path $npxPath)) {
    Write-Error 'npx.cmd not found under Program Files\nodejs'
}
& $npxPath -y @a-bonus/google-docs-mcp
