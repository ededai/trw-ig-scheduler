# TRW Auto-Sync — All Hubs, All Surfaces

**Goal:** any new article (Cole, Bryan, or Ed) automatically reflects on `/blog/`, `/news/` OR `/guides/` OR `/car-tips/`, and every relevant `/topics/<tag>/` page. Correct thumbnail. No misalignment.

**Locked decisions (Ed, 2026-05-15):**

| # | Decision |
|---|---|
| Category source | ~~WP tag prefix~~ → **`hub_classifier.json` in repo**. WP doesn't support tags or categories on Pages (Posts-only taxonomies; custom meta keys silently rejected without PHP registration). Mental model identical to tags: one slug → one category. Cole/Bryan append to this file at publish; Codi can do it via a tiny skill. |
| Thumbnail source | The article's hero image (selected by Ed + Bryan). For Cole's News: `news_featured_image.py` continues to handle. |
| QA gate | Prevent (1) misaligned thumbnail aspect, (2) wrong image on wrong article, (3) wrong hub tag, (4) wrong topic tag. |
| Sync direction | ADD-only. Slug changes / deletions stay manual. |

## Architecture

```
WP publish (Cole pipeline OR Bryan manual)
     │
     ├── article carries: hub-* tag + topic tags + hero image (featured_media)
     │
     ▼
GitHub Actions cron (trw-ig-scheduler/blog-cron.yml, daily 00:30 SGT)
     │
     ├── step 1a: sync_blog_hub_posts.py        → /blog/
     ├── step 1b: sync_category_hubs.py         → /news/ /guides/ /car-tips/
     ├── step 1c: sync_topic_pages.py           → /topics/<tag>/ for each tag
     ├── step 2 : refresh_trw_blog_index.py     → featured rotation + hero drift
     ├── step 3 : fix_article_featured_images   → og:image
     ├── step 4 : fix_article_schema_images     → JSON-LD
     └── step 5 : qa_gate.py                    → fails Telegram-alerts on broken cards
```

## Phases

1. **WP tag setup + backfill** — create 3 tags, assign every existing parent=0 article to one. Documented as Bryan/Cole publish checklist.
2. **Extend `sync_blog_hub_posts.py`** — read hub-* tag from WP (priority: WP tag > eyebrow div > default-Guides). Add `image_aspect_ok()` check (skip if not 16:10 ± 5%).
3. **New `sync_category_hubs.py`** — for each of pages 1772 (Guides) / 1774 (Car Tips) / 1776 (News), append missing cards whose hub-* tag matches. ADD-only.
4. **New `sync_topic_pages.py`** — for each non-hub WP tag on each article, ensure card appears on `/topics/<tag-slug>/`. Reuse `_resolve_topic_page_id()` pattern from `trw-cole/src/cole/hub_injector.py`.
5. **Wire into `daily_blog_refresh.sh`** — add as steps 1b and 1c.
6. **`qa_gate.py`** — runs LAST. For each card on each hub, verify (a) thumbnail aspect ratio is 16:10, (b) image filename matches article slug or featured_media id, (c) card's data-cat matches the article's hub-* tag, (d) /topics/<tag>/ presence == article's tag list. Telegram alert on any mismatch.
7. **Dry-run all** — confirm zero unexpected adds/changes. Then live.
8. **Memory + Bryan checklist** — `reference_blog_hub_automation.md` updated; new `feedback_bryan_publish_checklist.md`.

## Failure model

- Missing hub-* tag on a new article → article doesn't surface anywhere (loud silence). qa_gate.py catches and Telegram-alerts the orphan.
- Thumbnail not 16:10 → card not added on hubs. qa_gate.py alerts.
- Slug change on existing article → existing cards become broken links. Detected by audit script (already exists, runs bi-weekly).

## Out of scope (deliberate, per Ed)

- Auto-removal of cards when articles unpublish (manual cleanup).
- Auto-generation of thumbnails via nano-banana (Ed picks hero images manually).
- Real-time webhook (cron lag ≤24h is fine).
