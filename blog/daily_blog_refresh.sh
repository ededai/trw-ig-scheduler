#!/bin/bash
# Daily TRW blog maintenance — runs in GH Actions or locally.
# All scripts are idempotent — no-op when nothing has changed.
#
# Order matters:
#   1. refresh_trw_blog_index.py  — featured rotation + post-card hero drift
#   2. fix_article_featured_images — WP featured_media (drives og:image)
#   3. fix_article_schema_images   — JSON-LD Article.image inside wp:html

set -u
set -o pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$HERE/logs"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/cron_blog.log"
PY="${PYTHON_BIN:-python3}"

echo "" >> "$LOG"
echo "===== $(date -u +'%Y-%m-%dT%H:%M:%SZ') daily_blog_refresh start =====" >> "$LOG"

cd "$HERE"

overall_exit=0

run_step () {
    local label="$1"; shift
    echo "--- $label ---" | tee -a "$LOG"
    if ! "$@" 2>&1 | tee -a "$LOG"; then
        local rc=${PIPESTATUS[0]}
        echo "$label FAILED rc=$rc" | tee -a "$LOG"
        overall_exit=1
    fi
}

run_step "step 1: sync_blog_hub_posts (new posts + category fixes)" "$PY" sync_blog_hub_posts.py
run_step "step 2: refresh_trw_blog_index --apply" "$PY" refresh_trw_blog_index.py --apply
run_step "step 3: fix_article_featured_images --apply" "$PY" fix_article_featured_images.py --apply
run_step "step 4: fix_article_schema_images --apply" "$PY" fix_article_schema_images.py --apply

echo "===== $(date -u +'%Y-%m-%dT%H:%M:%SZ') daily_blog_refresh done (exit=$overall_exit) =====" >> "$LOG"
exit $overall_exit
