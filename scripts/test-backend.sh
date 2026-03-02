#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../src/backend"

echo "Running backend tests..."
uv run pytest ../../tests/backend/ -v --override-ini="asyncio_mode=auto"
