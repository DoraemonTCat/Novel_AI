#!/bin/bash
# Novel AI — Start Script (Linux/Mac)
# Usage:
#   ./start.sh                     -> Core services only
#   ./start.sh --with-ollama       -> + Ollama (Llama 3 8B)
#   ./start.sh --with-sd           -> + Stable Diffusion
#   ./start.sh --with-ollama --with-sd  -> All services

set -e

PROFILES=""
PULL_MODEL="llama3:8b"
WITH_OLLAMA=false
WITH_SD=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --with-ollama)
            PROFILES="$PROFILES --profile with-ollama"
            WITH_OLLAMA=true
            ;;
        --with-sd)
            PROFILES="$PROFILES --profile with-sd"
            WITH_SD=true
            ;;
        --model=*)
            PULL_MODEL="${arg#*=}"
            ;;
    esac
done

echo ""
echo "================================================"
echo "  Novel AI — AI-Powered Novel Writing Platform  "
echo "================================================"
echo ""

# Copy .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[!] Created .env from .env.example"
    echo "    Please configure your API keys in .env before continuing!"
    echo ""
    echo "    Required:"
    echo "      - GEMINI_API_KEY"
    echo "      - GOOGLE_OAUTH_CLIENT_ID"
    echo "      - GOOGLE_OAUTH_CLIENT_SECRET"
    echo ""
    exit 1
fi

# Start services
echo "[*] Starting services..."
docker compose $PROFILES up -d --build

# Pull Ollama model if needed
if [ "$WITH_OLLAMA" = true ]; then
    echo ""
    echo "[*] Waiting for Ollama to start..."
    sleep 15
    echo "[*] Pulling $PULL_MODEL model (this may take a while)..."
    docker compose exec ollama ollama pull $PULL_MODEL
fi

echo ""
echo "================================================"
echo "  Novel AI is running!                          "
echo "================================================"
echo ""
echo "  Frontend:     http://localhost:3000"
echo "  Backend API:  http://localhost:8000"
echo "  API Docs:     http://localhost:8000/docs"

if [ "$WITH_OLLAMA" = true ]; then
    echo "  Ollama:       http://localhost:11434"
fi
if [ "$WITH_SD" = true ]; then
    echo "  Stable Diff:  http://localhost:7860"
fi

echo ""
echo "  To stop: docker compose $PROFILES down"
echo ""
