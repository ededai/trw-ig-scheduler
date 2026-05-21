#!/usr/bin/env bash
# One-shot post-auth bootstrap. Run after `gh auth login -w`.
# - Creates the private GH repo
# - Pushes initial commit
# - Sets 3 secrets from ../tools/.env (never printed)
# - Triggers a manual run of the workflow to verify
set -euo pipefail
cd "$(dirname "$0")"

ENV_FILE="../tools/.env"
[[ -f "$ENV_FILE" ]] || { echo "ERROR: $ENV_FILE not found"; exit 1; }

# shellcheck disable=SC1090
set -a; . "$ENV_FILE"; set +a

echo "==> Creating private repo ededai/trw-ig-scheduler …"
gh repo create ededai/trw-ig-scheduler \
  --private \
  --source=. \
  --remote=origin \
  --description "TRW Instagram queue runner — cloud cron, free of local Mac uptime" \
  --push

echo "==> Setting secrets …"
gh secret set IG_USER_ID      --body "$IG_USER_ID"
gh secret set IG_ACCESS_TOKEN --body "$IG_ACCESS_TOKEN"
gh secret set IMGBB_API_KEY   --body "${IMGBB_API_KEY:-}"

echo "==> Triggering manual workflow run for verification …"
gh workflow run ig-cron.yml
sleep 4
gh run list --workflow=ig-cron.yml --limit 3

echo
echo "==> Repo URL: $(gh repo view --json url -q .url)"
echo "==> Done. Tail with: gh run watch"
