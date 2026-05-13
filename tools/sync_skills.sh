#!/usr/bin/env bash
# sync_skills.sh — Refresh data/skills/ from the source-of-truth on Ed's Mac.
#
# This script is meant to be run LOCALLY on Ed's Mac, NOT in CI. CI consumes
# the vendored snapshot that this script produced and that was committed to git.
#
# Usage: ./tools/sync_skills.sh
#
# Sources:
#   ~/.claude/skills/                  (system Claude Code skills)
#   ~/Desktop/Claude folder/Skills/    (TRW marketing pack)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$REPO_ROOT/data/skills"
SRC_CLAUDE="$HOME/.claude/skills"
SRC_DESKTOP="$HOME/Desktop/Claude folder/Skills"

if [ ! -d "$SRC_CLAUDE" ]; then
  echo "❌ Source not found: $SRC_CLAUDE" >&2
  exit 1
fi
if [ ! -d "$SRC_DESKTOP" ]; then
  echo "❌ Source not found: $SRC_DESKTOP" >&2
  exit 1
fi

echo "→ Syncing skills into $DEST"
mkdir -p "$DEST"

# The 10-skill stack — 8 folders covering all 10 components
# (claude-seo wraps seo-content + seo-google + seo-technical sub-agents)
SKILLS_FROM_CLAUDE=(
  "anti-ai-slop-writing"
  "avoid-ai-writing"
  "doc-coauthoring"
)
SKILLS_FROM_DESKTOP=(
  "copywriting"
  "copy-editing"
  "ai-seo"
  "claude-seo"
  "schema-markup"
)

# Stripped paths inside claude-seo (heavy + non-prompt content)
CLAUDE_SEO_STRIP=(
  ".git" ".github" ".devcontainer" ".claude-plugin" ".gitignore"
  "screenshots" "scripts" "extensions"
  "install.sh" "install.ps1" "uninstall.sh" "uninstall.ps1"
  "pyproject.toml" "requirements.txt"
  "LICENSE" "CITATION.cff" "CODEOWNERS" "SECURITY.md"
  "claude-seo-v1.8.0-release.html"
)

for skill in "${SKILLS_FROM_CLAUDE[@]}"; do
  src="$SRC_CLAUDE/$skill"
  dst="$DEST/$skill"
  if [ ! -d "$src" ]; then
    echo "  ⚠️  Skipping $skill (source missing: $src)"
    continue
  fi
  echo "  ✔  $skill (from ~/.claude/skills/)"
  rm -rf "$dst"
  cp -R "$src" "$dst"
done

for skill in "${SKILLS_FROM_DESKTOP[@]}"; do
  src="$SRC_DESKTOP/$skill"
  dst="$DEST/$skill"
  if [ ! -d "$src" ]; then
    echo "  ⚠️  Skipping $skill (source missing: $src)"
    continue
  fi
  echo "  ✔  $skill (from Desktop/Claude folder/Skills/)"
  rm -rf "$dst"
  cp -R "$src" "$dst"
done

# Strip bloat from claude-seo
if [ -d "$DEST/claude-seo" ]; then
  echo "→ Stripping claude-seo bloat..."
  for p in "${CLAUDE_SEO_STRIP[@]}"; do
    rm -rf "$DEST/claude-seo/$p"
  done
fi

# Remove .DS_Store files anywhere
/usr/bin/find "$DEST" -name '.DS_Store' -type f -delete

# Write timestamp stamp
cat > "$DEST/STAMP.txt" <<EOF
last_sync: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
synced_by: $(whoami)@$(hostname)
source_paths:
  - $SRC_CLAUDE/{anti-ai-slop-writing,avoid-ai-writing,doc-coauthoring}
  - $SRC_DESKTOP/{copywriting,copy-editing,ai-seo,claude-seo,schema-markup}
EOF

# Final size report
total_size=$(du -sh "$DEST" | awk '{print $1}')
echo
echo "✅ Sync complete. Total size: $total_size"
echo "   Commit + push when ready:"
echo "     git add data/skills/"
echo "     git commit -m 'Refresh vendored writing+SEO skills'"
echo "     git push"
