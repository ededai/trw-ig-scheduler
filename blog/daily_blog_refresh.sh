#!/bin/bash
# Daily TRW blog maintenance — runs in GH Actions or locally.
# All scripts are idempotent — no-op when nothing has changed.
#
# Order matters:
#   1. refresh_trw_blog_index.py  — featured rotation + post-card hero drift
#   2. fix_article_featured_images — WP featured_media (drives og:image)
#   3. fix_article_schema_images   — JSON-LD Article.image inside wp:html

set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$HERE/logs"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/cron_blog.log"
PY="${PYTHON_BIN:-python3}"

echo "" >> "$LOG"
echo "===== $(date -u +'%Y-%m-%dT%H:%M:%SZ') daily_blog_refresh start =====" >> "$LOG"

cd "$HERE"

echo "--- step 1: refresh_trw_blog_index --apply ---" >> "$LOG"
"$PY" refresh_trw_blog_index.py --apply >> "$LOG" 2>&1 || echo "step 1 exit=$?" >> "$LOG"

echo "--- step 2: fix_article_featured_images --apply ---" >> "$LOG"
"$PY" fix_article_featured_images.py --apply >> "$LOG" 2>&1 || echo "step 2 exit=$?" >> "$LOG"

echo "--- step 3: fix_article_schema_images --apply ---" >> "$LOG"
"$PY" fix_article_schema_images.py --apply >> "$LOG" 2>&1 || echo "step 3 exit=$?" >> "$LOG"

echo "===== $(date -u +'%Y-%m-%dT%H:%M:%SZ') daily_blog_refresh done =====" >> "$LOG"
