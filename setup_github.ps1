# PowerShell script to set up GitHub repository
# Run this after creating the repo on GitHub

Write-Host "Setting up GitHub repository..." -ForegroundColor Green

# Check if remote already exists
$remoteExists = git remote get-url origin 2>$null
if ($remoteExists) {
    Write-Host "Remote 'origin' already exists. Removing..." -ForegroundColor Yellow
    git remote remove origin
}

# Add remote (replace with your GitHub username if different)
$repoName = "project_work_llm"
Write-Host ""
Write-Host "Please provide your GitHub username:" -ForegroundColor Cyan
$username = Read-Host

if ([string]::IsNullOrWhiteSpace($username)) {
    Write-Host "Username not provided. Please run manually:" -ForegroundColor Red
    Write-Host "  git remote add origin https://github.com/YOUR_USERNAME/project_work_llm.git" -ForegroundColor Yellow
    Write-Host "  git branch -M main" -ForegroundColor Yellow
    Write-Host "  git push -u origin main" -ForegroundColor Yellow
    exit
}

$remoteUrl = "https://github.com/$username/$repoName.git"
Write-Host ""
Write-Host "Adding remote: $remoteUrl" -ForegroundColor Cyan
git remote add origin $remoteUrl

Write-Host "Setting branch to 'main'..." -ForegroundColor Cyan
git branch -M main

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Green
Write-Host "1. Create the repository on GitHub (if not already created):" -ForegroundColor Yellow
Write-Host "   - Go to: https://github.com/new" -ForegroundColor Yellow
Write-Host "   - Repository name: project_work_llm" -ForegroundColor Yellow
Write-Host "   - Set to Private" -ForegroundColor Yellow
Write-Host "   - DO NOT initialize with README, .gitignore, or license" -ForegroundColor Yellow
Write-Host "   - Click 'Create repository'" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Then run:" -ForegroundColor Yellow
Write-Host "   git push -u origin main" -ForegroundColor Cyan
