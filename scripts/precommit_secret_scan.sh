#!/usr/bin/env bash
# Simple pre-commit secret scan to prevent committing API keys/tokens
# Blocks commit if suspicious patterns are found in staged changes.
# Install with: scripts/install_precommit_hook.sh

set -euo pipefail

red() { printf "\033[31m%s\033[0m\n" "$*"; }
yellow() { printf "\033[33m%s\033[0m\n" "$*"; }

# Files to scan (added/copied/modified)
mapfile -t FILES < <(git diff --cached --name-only --diff-filter=ACM | tr -d '\r')

if [[ ${#FILES[@]} -eq 0 ]]; then
  exit 0
fi

SUSPICIOUS=()

# Patterns to flag (extend as needed)
# - xAI tokens (start with xai-)
# - Direct assignments to XAI_API_KEY / ALPHA_VANTAGE_API_KEY
# - Bearer tokens with xai-
PATTERN_XAI_TOKEN='xai-[A-Za-z0-9]{20,}'
PATTERN_XAI_ASSIGN='\bXAI_API_KEY\b\s*[:=]\s*[\"\']?[A-Za-z0-9_-]{16,}'
PATTERN_ALPHA_ASSIGN='\bALPHA_VANTAGE_API_KEY\b\s*[:=]\s*[\"\']?[A-Za-z0-9_-]{8,}'
PATTERN_BEARER_XAI='Bearer\s+xai-[A-Za-z0-9]+'

# Common provider patterns
PATTERN_AWS='\bAKIA[0-9A-Z]{16}\b'
PATTERN_GITHUB='\bghp_[A-Za-z0-9]{36,}\b'
PATTERN_GOOGLE='\bAIza[0-9A-Za-z\-_]{35}\b'
PATTERN_STRIPE='\bsk_(live|test)_[A-Za-z0-9]{24,}\b'
PATTERN_SENDGRID='\bSG\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}\b'
PATTERN_SLACK='\bxox[baprs]-[A-Za-z0-9-]{10,}\b'
PATTERN_OPENAI='\bsk-[A-Za-z0-9]{20,}\b|\bOPENAI_API_KEY\b\s*[:=]\s*[\"\']?[A-Za-z0-9_-]{16,}'
PATTERN_GENERIC_ASSIGN='\b(API_KEY|SECRET|TOKEN|ACCESS_TOKEN)\b\s*[:=]\s*[\"\'][A-Za-z0-9_\-]{12,}[\"\']'

should_skip() {
  local f="$1"
  case "$f" in
    *.md|*.MD|*.png|*.jpg|*.jpeg|*.gif|*.pdf|*.svg|*.ico|*.zip|*.gz) return 0 ;;
    .env.example|LICENSE|COPYING) return 0 ;;
    .github/*) return 0 ;;
  esac
  return 1
}

for f in "${FILES[@]}"; do
  if should_skip "$f"; then
    continue
  fi
  # Get staged contents of the file
  if ! content=$(git show ":$f" 2>/dev/null); then
    continue
  fi
  # Scan with patterns
  if grep -E -n -q "$PATTERN_XAI_TOKEN|$PATTERN_XAI_ASSIGN|$PATTERN_ALPHA_ASSIGN|$PATTERN_BEARER_XAI|$PATTERN_AWS|$PATTERN_GITHUB|$PATTERN_GOOGLE|$PATTERN_STRIPE|$PATTERN_SENDGRID|$PATTERN_SLACK|$PATTERN_OPENAI|$PATTERN_GENERIC_ASSIGN" <<<"$content"; then
    SUSPICIOUS+=("$f")
  fi
done

if [[ ${#SUSPICIOUS[@]} -gt 0 ]]; then
  red "\n✋ Secret-like patterns detected in staged files:"
  for f in "${SUSPICIOUS[@]}"; do
    yellow " - $f"
  done
  cat <<'EOF'

Refusing to commit. Please remove secrets and use environment variables instead.
- For xAI: export XAI_API_KEY and do NOT commit it.
- For Alpha Vantage: export ALPHA_VANTAGE_API_KEY and do NOT commit it.

To override (NOT RECOMMENDED):
  git commit --no-verify
EOF
  exit 1
fi

exit 0
