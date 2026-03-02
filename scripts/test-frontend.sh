#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../src/frontend"

echo "Running frontend tests..."
npm test
