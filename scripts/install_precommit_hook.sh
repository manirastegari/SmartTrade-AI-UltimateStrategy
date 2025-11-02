#!/usr/bin/env bash
# Install the secret scan pre-commit hook into .git/hooks
set -euo pipefail

HOOK_DIR=".git/hooks"
HOOK_FILE="$HOOK_DIR/pre-commit"
SCRIPT="scripts/precommit_secret_scan.sh"

if [[ ! -d "$HOOK_DIR" ]]; then
  echo "This script must be run from the repository root (where .git exists)." >&2
  exit 1
fi

chmod +x "$SCRIPT"
cp "$SCRIPT" "$HOOK_FILE"
chmod +x "$HOOK_FILE"

echo "✅ Installed pre-commit hook: $HOOK_FILE"
echo "It will block commits that include API keys or tokens."
