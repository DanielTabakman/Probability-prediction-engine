<#!
  One-time (or repeat-safe) GitHub configuration for zero-touch ship:
  - Enables "Allow auto-merge" on the repository.
  - Creates or updates a branch ruleset for `refs/heads/main`:
    PR required (0 approving reviews), required check "CI / pytest", no force-push.

  Prerequisites:
  - GitHub CLI: https://cli.github.com/ (winget: GitHub.cli)
  - Authenticated: run `gh auth login` (HTTPS + github.com) with repo admin scope.
  - The CI workflow must have run at least once on a PR or on `main` so the check
    name "CI / pytest" exists when you require it (GitHub UI can also pick the check).

  Usage (from repo root):
    powershell -ExecutionPolicy Bypass -File scripts/enable_github_zero_touch.ps1
#>
$ErrorActionPreference = "Stop"

function Get-GhExe {
    $cmd = Get-Command gh -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $default = "C:\Program Files\GitHub CLI\gh.exe"
    if (Test-Path $default) { return $default }
    throw "GitHub CLI (gh) not found. Install from https://cli.github.com/ or winget install GitHub.cli"
}

$gh = Get-GhExe

$ErrorActionPreference = "Continue"
& $gh auth status *> $null
$authOk = ($LASTEXITCODE -eq 0)
$ErrorActionPreference = "Stop"

if (-not $authOk) {
    Write-Host "Not logged in. Run first in this repo:" -ForegroundColor Yellow
    Write-Host "  gh auth login -h github.com -p https -w" -ForegroundColor Cyan
    exit 1
}

$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
    $slug = & $gh repo view --json nameWithOwner -q .nameWithOwner 2>&1
    if ($LASTEXITCODE -ne 0) { throw "gh repo view failed: $slug" }
    $isPrivateStr = & $gh repo view --json isPrivate -q .isPrivate 2>&1
    if ($LASTEXITCODE -ne 0) { throw "gh repo view isPrivate failed: $isPrivateStr" }
}
finally {
    Pop-Location
}

$isPrivate = ($isPrivateStr -eq 'true')

Write-Host "Repository: $slug" -ForegroundColor Green

# 1) Allow auto-merge (boolean via JSON body; -f allow_auto_merge=true is unreliable)
Write-Host "Enabling allow_auto_merge..." -ForegroundColor Cyan
$patchPath = [System.IO.Path]::GetTempFileName()
try {
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($patchPath, '{"allow_auto_merge":true}', $utf8NoBom)
    $patchOut = & $gh api "repos/$slug" -X PATCH --input $patchPath 2>&1
    if ($LASTEXITCODE -ne 0) { throw "PATCH allow_auto_merge failed: $patchOut" }
    $repoObj = $patchOut | ConvertFrom-Json
    if (-not $repoObj.allow_auto_merge) {
        Write-Host "  Warning: API returned allow_auto_merge=false." -ForegroundColor Yellow
        if ($isPrivate) {
            Write-Host "  On GitHub Free, auto-merge and branch protection for private repos often require GitHub Pro" -ForegroundColor Yellow
            Write-Host "  or a public repository. Enable auto-merge manually if the UI allows: Settings -> General -> Pull requests." -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "  OK (allow_auto_merge is true)" -ForegroundColor Green
    }
}
finally {
    Remove-Item -Force -ErrorAction SilentlyContinue $patchPath
}

# 2) Ruleset body
$rulesetName = "PPE zero-touch main"
$ruleset = @{
    name        = $rulesetName
    target      = "branch"
    enforcement = "active"
    conditions  = @{
        ref_name = @{
            include = @("refs/heads/main")
            exclude = @()
        }
    }
    rules       = @(
        @{ type = "non_fast_forward" }
        @{
            type       = "pull_request"
            parameters = @{
                allowed_merge_methods             = @("merge", "squash", "rebase")
                dismiss_stale_reviews_on_push     = $false
                require_code_owner_review         = $false
                require_last_push_approval        = $false
                required_approving_review_count   = 0
                required_review_thread_resolution = $false
            }
        }
        @{
            type       = "required_status_checks"
            parameters = @{
                strict_required_status_checks_policy = $true
                required_status_checks               = @(
                    @{
                        context        = "CI / pytest"
                        integration_id = 15368
                    }
                )
            }
        }
    )
}

$jsonPath = [System.IO.Path]::GetTempFileName()
try {
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($jsonPath, ($ruleset | ConvertTo-Json -Depth 12 -Compress), $utf8NoBom)

    $ErrorActionPreference = "Continue"
    $existing = & $gh api "repos/$slug/rulesets" 2>&1
    $rulesetsExit = $LASTEXITCODE
    $ErrorActionPreference = "Stop"

    if ($rulesetsExit -ne 0) {
        $errText = "$existing"
        if ($errText -match '403|Upgrade to GitHub Pro|make this repository public') {
            Write-Host "" 
            Write-Host "Rulesets API returned 403 (common for private repos on GitHub Free)." -ForegroundColor Yellow
            Write-Host "Options: (1) GitHub Pro / Team for this account or org, (2) make the repo public if acceptable," -ForegroundColor Yellow
            Write-Host "or (3) add branch protection manually: Settings -> Rules -> Rulesets (or Branch protection) for main." -ForegroundColor Yellow
            Write-Host "Require PR + status check CI / pytest + 0 required reviewers; then use Enable auto-merge on each PR if available." -ForegroundColor Yellow
            exit 0
        }
        throw "GET rulesets failed: $existing"
    }
    $rulesets = $existing | ConvertFrom-Json
    if ($rulesets -isnot [System.Array]) { $rulesets = @($rulesets) }
    $match = $rulesets | Where-Object { $_.name -eq $rulesetName } | Select-Object -First 1

    if ($match) {
        $id = $match.id
        Write-Host "Updating ruleset id=$id ..." -ForegroundColor Cyan
        & $gh api "repos/$slug/rulesets/$id" -X PUT --input $jsonPath
        if ($LASTEXITCODE -ne 0) { throw "PUT rulesets/$id failed" }
    }
    else {
        Write-Host "Creating ruleset '$rulesetName'..." -ForegroundColor Cyan
        & $gh api "repos/$slug/rulesets" -X POST --input $jsonPath
        if ($LASTEXITCODE -ne 0) { throw "POST rulesets failed" }
    }
}
finally {
    Remove-Item -Force -ErrorAction SilentlyContinue $jsonPath
}

Write-Host "Done. In GitHub: confirm Settings -> General -> Pull requests -> Allow auto-merge is on." -ForegroundColor Green
Write-Host "On each PR, use 'Enable auto-merge' (or the API) so merges happen when CI is green." -ForegroundColor Green
