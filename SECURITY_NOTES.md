# Secrets and Public Repos

This repository is configured to avoid committing secrets. Before making it public, follow these steps.

## What we changed
- Removed hardcoded API keys from `api_keys.py`. The file now reads from environment variables only.
- `.gitignore` already excludes `.env` and `api_keys.py` to prevent accidental commits.
- Added a local pre-commit hook (`scripts/precommit_secret_scan.sh`) that blocks commits containing secret-like strings.
- Added a GitHub Action (`.github/workflows/secret-scan.yml`) to scan pushes/PRs using Gitleaks.

## How to enable local protection
Install the pre-commit hook locally (run from repo root):

```bash
bash scripts/install_precommit_hook.sh
```

This hook will block commits if staged changes include patterns like `xai-...` or assignments to `XAI_API_KEY`.

## How to use environment variables
Export your keys locally (macOS zsh):

```bash
echo 'export XAI_API_KEY="<your_xai_key>"' >> ~/.zshrc
echo 'export ALPHA_VANTAGE_API_KEY="<your_alpha_vantage_key>"' >> ~/.zshrc
source ~/.zshrc
```

Or use a non-committed `.env` and a loader (if you add one). Do not commit `.env`.

## Recommended: rotate old keys
A key that was committed should be considered compromised.
- Rotate `XAI_API_KEY` and `ALPHA_VANTAGE_API_KEY` in their provider dashboards.
- Optionally scrub history using `git filter-repo` or BFG to purge old secrets.

## Optional: scrub history
If you want, run a history purge (replace placeholders):

```bash
# Install (one-time): brew install git-filter-repo
# Remove all occurrences of literal values in history (examples)
# git filter-repo --invert-paths --path api_keys.py --force

# Or redact specific patterns (advanced; ensure you have remote + backups before proceeding)
# See: https://github.com/newren/git-filter-repo
```

## CI protection
Making the repo public will activate the GitHub Action. If a PR introduces secrets, the action will fail.
