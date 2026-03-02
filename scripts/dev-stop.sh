#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Stopping CampaignLauncher services..."
docker compose down
echo "Services stopped."
