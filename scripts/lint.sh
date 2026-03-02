#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../src/frontend"

echo "Running linter and formatter checks..."
npm run lint
echo "Lint passed."
