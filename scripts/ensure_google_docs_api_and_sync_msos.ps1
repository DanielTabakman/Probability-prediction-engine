# Enable Google Docs API (one-time browser click) then push PPE / MSOS Repo Truth — Live Mirror.
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $repoRoot
$project = '103338530342'
$enableUrl = "https://console.developers.google.com/apis/api/docs.googleapis.com/overview?project=$project"
Write-Host 'If Docs API is not enabled yet, browser will open - click ENABLE once.'
Start-Process $enableUrl
$env:PYTHONPATH = $repoRoot
$maxAttempts = 12
for ($i = 1; $i -le $maxAttempts; $i++) {
    Write-Host "MSOS sync attempt $i/$maxAttempts..."
    & py -3.11 scripts/sync_msos_repo_truth.py --repo-root $repoRoot
    if ($LASTEXITCODE -eq 0) {
        $reportPath = Join-Path $repoRoot 'artifacts/control_plane/msos_sync_report.json'
        if (Test-Path $reportPath) {
            $report = Get-Content $reportPath -Raw | ConvertFrom-Json
            if ($report.passed -and -not $report.skipped) {
                Write-Host 'Done. PPE / MSOS Repo Truth — Live Mirror updated in Google Docs.'
                exit 0
            }
        }
    }
    Start-Sleep -Seconds 15
}
Write-Error ('MSOS sync did not succeed. Enable Google Docs API then re-run: ' + $enableUrl)
