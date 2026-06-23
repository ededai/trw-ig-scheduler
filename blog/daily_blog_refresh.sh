#!/bin/bash
# Daily TRW blog maintenance — runs in GH Actions or locally.
# All scripts are idempotent — no-op when nothing has changed.
#
# Order matters:
#   1. sync_blog_hub_posts          — new posts added to /blog/ from WP categories
#   2. refresh_trw_blog_index       — featured rotation + post-card hero drift
#   3. fix_article_featured_images  — WP featured_media (drives og:image)
#   4. fix_article_schema_images    — JSON-LD Article.image inside wp:html
#   5. sync_category_pages          — new posts added to /guides/ /car-tips/ /news/ (2026-05-17 fix #4)
#   6. refresh_card_excerpts        — clean every card's <p> from WP excerpt (2026-05-17 fix #6)
#   7. notify_thumb_check           — Telegram sanity check on news featured_media (2026-05-17 fix #7)

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
# step 5 sync_category_pages is DISABLED pending allowlist tightening.
# First run (2026-05-17) discovered 42 unwanted WP-category-tagged pages
# that aren't actual articles. Ed: clean up WP categories OR we add an
# allowlist (e.g., slug-must-have-news_post_renderer-output, slug-must-be-in-SLUG_TO_CATEGORY).
# Until then, /guides/ /car-tips/ /news/ are rebuilt manually via
# `python3 wp-import/push_category_pages.py` (curated manifest only).
# run_step "step 5: sync_category_pages (/guides/ /car-tips/ /news/)" "$PY" sync_category_pages.py
run_step "step 5b: refresh_topic_tags_json (auto-merge from WP tags)" "$PY" refresh_topic_tags_json.py
run_step "step 5c: sync_topic_pages (/topics/{tag}/ cards)" "$PY" sync_topic_pages.py
run_step "step 5d: refresh_search_corpus (keyworded site search on all search pages)" "$PY" refresh_search_corpus.py --apply
run_step "step 6: refresh_card_excerpts (defensive sweep)" "$PY" refresh_card_excerpts.py
run_step "step 7: notify_thumb_check (Telegram sanity check)" "$PY" notify_thumb_check.py

echo "===== $(date -u +'%Y-%m-%dT%H:%M:%SZ') daily_blog_refresh done (exit=$overall_exit) =====" >> "$LOG"
exit $overall_exit
