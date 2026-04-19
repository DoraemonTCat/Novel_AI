# Novel AI - Start Script (Windows)
# Usage:
#   .\start.ps1                          -> Core services only (Gemini)
#   .\start.ps1 -WithOllama              -> + Ollama (Llama 3 8B)
#   .\start.ps1 -WithSD                  -> + Stable Diffusion (covers)
#   .\start.ps1 -WithOllama -WithSD      -> All services

param(
    [switch]$WithOllama,
    [switch]$WithSD,
    [string]$PullModel = "llama3:8b"
)

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Novel AI - AI-Powered Novel Writing Platform  " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Copy .env if not exists
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "[!] Created .env from .env.example" -ForegroundColor Yellow
    Write-Host "    Please configure your API keys in .env before continuing!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "    Required:" -ForegroundColor Yellow
    Write-Host "      - GEMINI_API_KEY" -ForegroundColor Yellow
    Write-Host "      - GOOGLE_OAUTH_CLIENT_ID" -ForegroundColor Yellow
    Write-Host "      - GOOGLE_OAUTH_CLIENT_SECRET" -ForegroundColor Yellow
    Write-Host ""
    return
}

# Build profiles list
$profiles = @()
if ($WithOllama) { $profiles += "--profile"; $profiles += "with-ollama" }
if ($WithSD) { $profiles += "--profile"; $profiles += "with-sd" }

# Start services
Write-Host "[*] Starting services..." -ForegroundColor Green
if ($profiles.Count -gt 0) {
    docker compose $profiles up -d --build
} else {
    docker compose up -d --build
}

# Pull Ollama model if needed
if ($WithOllama) {
    Write-Host ""
    Write-Host "[*] Waiting for Ollama to start..." -ForegroundColor Green
    Start-Sleep -Seconds 15
    Write-Host "[*] Pulling $PullModel model (this may take a while)..." -ForegroundColor Green
    docker compose exec ollama ollama pull $PullModel
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  Novel AI is running!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend:     http://localhost:3000" -ForegroundColor White
Write-Host "  Backend API:  http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:     http://localhost:8000/docs" -ForegroundColor White
if ($WithOllama) {
    Write-Host "  Ollama:       http://localhost:11434" -ForegroundColor White
}
if ($WithSD) {
    Write-Host "  Stable Diff:  http://localhost:7860" -ForegroundColor White
}
Write-Host ""
$stopCmd = "docker compose"
if ($profiles.Count -gt 0) { $stopCmd += " " + ($profiles -join " ") }
$stopCmd += " down"
Write-Host "  To stop: $stopCmd" -ForegroundColor DarkGray
Write-Host ""
