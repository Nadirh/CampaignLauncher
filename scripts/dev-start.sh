#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Starting CampaignLauncher services..."
docker compose up --build -d
echo "Services started. Frontend: http://localhost:3000 | Backend: http://localhost:8000"
