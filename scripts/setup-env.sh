#!/usr/bin/env bash
# Generates .env.local from .env.example, substituting any matching
# Codespaces secrets (environment variables) for placeholder values.
# Safe to re-run -- overwrites .env.local each time.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EXAMPLE="$REPO_ROOT/.env.example"
OUTPUT="$REPO_ROOT/.env.local"

if [ ! -f "$EXAMPLE" ]; then
  echo "Error: $EXAMPLE not found"
  exit 1
fi

substituted=0
total=0

while IFS= read -r line; do
  # Pass through comments and blank lines
  if [[ "$line" =~ ^#.* ]] || [[ -z "$line" ]]; then
    echo "$line"
    continue
  fi

  key="${line%%=*}"
  default_value="${line#*=}"
  total=$((total + 1))

  # If the variable exists in the environment, use it
  if [ -n "${!key+x}" ] && [ -n "${!key}" ]; then
    echo "${key}=${!key}"
    substituted=$((substituted + 1))
  else
    echo "$line"
  fi
done < "$EXAMPLE" > "$OUTPUT"

echo "Generated $OUTPUT ($substituted/$total variables from environment, rest kept as defaults)"
