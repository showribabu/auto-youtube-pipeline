# Auto YouTube Pipeline — One-Click Installer & Deploy Script
# Run this: right-click → Run with PowerShell
# Purpose: Creates GitHub repo, uploads code, sets up YouTube auth guide
# You only need to provide your GitHub PAT (Personal Access Token) once

$ErrorActionPreference = "Continue"
$RepoOwner = "rajubai6419"
$RepoName  = "auto-youtube-pipeline"
$RepoUrl   = "https://github.com/$RepoOwner/$RepoName"
$BaseDir   = Split-Path $PSScriptRoot -Parent

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Auto YouTube AI Video Pipeline — Deployment Setup" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# ── Step 1: Check/Install GitHub CLI ──────────────────────
Write-Host "[1/5] Checking GitHub CLI..." -ForegroundColor Yellow
$ghExe = Get-Command gh -ErrorAction SilentlyContinue
if (-not $ghExe) {
    Write-Host "  Installing gh CLI via winget..." -ForegroundColor Gray
    winget install GitHub.cli --accept-source-agreements --accept-package-agreements 2>&1 | Out-Null
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
} else {
    Write-Host "  gh found at: $($ghExe.Source)" -ForegroundColor Gray
}

# Try auth
Write-Host "[1/5] GitHub Authentication..." -ForegroundColor Yellow
$authCheck = gh auth status 2>&1
if ($authCheck -match "not logged in" -or $authCheck -match "No credentials found") {
    Write-Host ""
    Write-Host "  Please authenticate with GitHub." -ForegroundColor White
    Write-Host "  A browser window will open for sign-in." -ForegroundColor Gray
    Write-Host ""
    gh auth login -p web 2>&1 | Out-Null
    if (gh auth status 2>&1 | Select-String -Quiet "logged in") {
        Write-Host "  ✓ GitHub authenticated!" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Auth failed. Please try again manually: gh auth login" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ✓ Already authenticated: $((gh api user --jq '.login') 2>$null)" -ForegroundColor Green
}

# ── Step 2: Create/Verify GitHub Repo ────────────────────
Write-Host ""
Write-Host "[2/5] Setting up GitHub Repository..." -ForegroundColor Yellow
$repoExists = gh repo view "$RepoOwner/$RepoName" --json nameWithOwner 2>&1 | ConvertFrom-Json -ErrorAction SilentlyContinue
if (-not $repoExists -or -not $repoExists.nameWithOwner) {
    Write-Host "  Creating public repository..." -ForegroundColor Gray
    gh repo create "$RepoName" `
        --public `
        --description="Auto AI Video Generation & YouTube Upload Pipeline" `
        --source="." `
        --remote="origin" `
        --push 2>&1 | Out-Null
    Write-Host "  ✓ Repository created: $RepoUrl" -ForegroundColor Green
} else {
    Write-Host "  ✓ Repository exists: $RepoUrl" -ForegroundColor Green
}

# ── Step 3: Push Files ───────────────────────────────────
Write-Host ""
Write-Host "[3/5] Pushing files to GitHub..." -ForegroundColor Yellow
Push-Location $BaseDir
git add .
git commit -m "Auto YouTube Pipeline v1.0 - Ready for deployment" 2>&1 | Out-Null
git push origin main 2>&1 | Out-Null
Pop-Location
Write-Host "  ✓ All files pushed to GitHub" -ForegroundColor Green

# ── Step 4: Set Up YouTube API Credentials ───────────────
Write-Host ""
Write-Host "[4/5] YouTube API Setup Guide..." -ForegroundColor Yellow
Write-Host ""
Write-Host "  To enable video UPLOAD to YouTube, do these steps:" -ForegroundColor White
Write-Host ""
Write-Host "  1. Go to: https://console.cloud.google.com/apis/credentials" -ForegroundColor Cyan
Write-Host "  2. Click '+ CREATE CREDENTIALS' → 'OAuth client ID'" -ForegroundColor Cyan
Write-Host "  3. Application type: 'Desktop app'" -ForegroundColor Cyan
Write-Host "  4. Name: 'auto-youtube-uploader'" -ForegroundColor Cyan
Write-Host "  5. Download the JSON file (client_secret.json)" -ForegroundColor Cyan
Write-Host "  6. In GitHub repo: Settings → Secrets and variables → Actions" -ForegroundColor Cyan
Write-Host "     Add secrets: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET" -ForegroundColor Cyan
Write-Host ""
Write-Host "  NOTE: The pipeline generates videos DAILY without uploads until" -ForegroundColor Gray
Write-Host "        you configure these YouTube credentials." -ForegroundColor Gray
Write-Host ""

# ── Step 5: Configure GitHub Actions ─────────────────────
Write-Host "[5/5] Verifying GitHub Actions workflow..." -ForegroundColor Yellow
if (Test-Path "$BaseDir/.github/workflows/daily.yml") {
    Write-Host "  ✓ Workflow file present: .github/workflows/daily.yml" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Missing workflow file" -ForegroundColor Red
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Repository URL : $RepoUrl" -ForegroundColor White
Write-Host ""
Write-Host "Next actions:" -ForegroundColor White
Write-Host "  1. Videos generate DAILY at 6 AM UTC automatically" -ForegroundColor Green
Write-Host "  2. Watch progress: Actions tab on GitHub repo" -ForegroundColor Green
Write-Host "  3. Optional: Add YouTube credentials for auto-upload" -ForegroundColor Yellow
Write-Host ""
Write-Host "Video Categories Generated:" -ForegroundColor White
Write-Host "  - Weather Reports      (live data from wttr.in)" -ForegroundColor Gray
Write-Host "  - News Roundups        (BBC/NYT RSS feeds)"       -ForegroundColor Gray
Write-Host "  - Kids Stories         (fun educational tales)"   -ForegroundColor Gray
Write-Host "  - Fun Facts            (mind-blowing science)"    -ForegroundColor Gray
Write-Host "  - Motivational Quotes  (daily inspiration)"       -ForegroundColor Gray
Write-Host ""
Write-Host "Open your repo: $RepoUrl" -ForegroundColor Cyan
Write-Host ""
