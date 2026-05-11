#!/usr/bin/env python3
"""TRW Bi-weekly Content Sync Audit (cloud edition).

Read-only. Scans key pages for drift and reports anything missing or stale:

  1. /blog/ index — does it list every published blog post?
  2. /topics/ hub — does it list every tag page that exists?
  3. /topics/<slug>/ — does each tag page list at least one post?
  4. /guides/, /car-tips/, /news/ category archives — reachable?
  5. Homepage Car Tips & Guides carousel — recent posts surfaced?

Reads WORDPRESS_API_URL / WORDPRESS_USERNAME / WORDPRESS_PASSWORD from env
(GitHub Actions secrets in the cloud, .env locally).

Optional Telegram notification on drift (TG_BOT_TOKEN / TG_CHAT_ID env).

Schedule: 1st + 15th of each month at 02:30 SGT (= 18:30 UTC the day before).

Run:
  python3 biweekly_content_sync_check.py
  python3 biweekly_content_sync_check.py --json
"""

import json
import base64
import re
import os
import sys
import datetime as dt
from pathlib import Path
from urllib import request, error, parse

SITE = os.environ.get("WORDPRESS_API_URL", "https://therightworkshop.com").rstrip("/")
USER = os.environ.get("WORDPRESS_USERNAME", "")
PASS = os.environ.get("WORDPRESS_PASSWORD", "")
TG_BOT = os.environ.get("TG_BOT_TOKEN", "")
TG_CHAT = os.environ.get("TG_CHAT_ID", "")

HOMEPAGE_ID = 90
BLOG_PAGE_ID = 475
TOPICS_HUB_ID = 1597

CATEGORY_PAGES = [
    ("Guides",   "/guides/"),
    ("Car Tips", "/car-tips/"),
    ("News",     "/news/"),
]


def log(msg: str) -> None:
    print(f"[{dt.datetime.now().isoformat(timespec='seconds')}] {msg}")


def basic_auth() -> str:
    return "Basic " + base64.b64encode(f"{USER}:{PASS}".encode()).decode()


def wp_get(path: str):
    url = f"{SITE}/wp-json/wp/v2{path}"
    req = request.Request(url, headers={"Authorization": basic_auth()})
    try:
        with request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    except error.HTTPError as e:
        log(f"  HTTP {e.code} on {path}")
        return None
    except Exception as e:
        log(f"  ERR on {path}: {e}")
        return None


def fetch_page_html(page_id: int) -> str:
    p = wp_get(f"/pages/{page_id}?context=edit&_fields=content")
    if not p:
        return ""
    return p["content"]["raw"]


def fetch_url_html(url: str) -> str:
    try:
        req = request.Request(url, headers={"User-Agent": "Mozilla/5.0 TRW-Audit"})
        with request.urlopen(req, timeout=60) as r:
            return r.read().decode("utf-8", "replace")
    except Exception as e:
        log(f"  fetch ERR {url}: {e}")
        return ""


def list_all_pages():
    out, page = [], 1
    while True:
        data = wp_get(f"/pages?per_page=100&page={page}&_fields=id,slug,title,link,parent,status,date")
        if not data:
            break
        out.extend(data)
        if len(data) < 100:
            break
        page += 1
    return out


def audit_blog_index(blog_post_pages):
    log("Auditing /blog/ index...")
    blog_html = fetch_page_html(BLOG_PAGE_ID)
    listed = set(re.findall(r'<a class="post-card"[^>]*href="/([a-z0-9\-]+)/"', blog_html))
    expected = {p["slug"] for p in blog_post_pages}
    missing = expected - listed
    extra = listed - expected
    log(f"  /blog/ lists {len(listed)} cards, expected {len(expected)} blog posts")
    if missing: log(f"  MISSING from /blog/: {sorted(missing)}")
    if extra:   log(f"  EXTRA on /blog/: {sorted(extra)}")
    return {"missing": sorted(missing), "extra": sorted(extra), "listed": len(listed), "expected": len(expected)}


def audit_topics_hub(tag_pages):
    log("Auditing /topics/ hub...")
    hub_html = fetch_page_html(TOPICS_HUB_ID)
    listed = set(re.findall(r'href="https?://therightworkshop.com/topics/([a-z0-9\-]+)/?"', hub_html))
    expected = {p["slug"] for p in tag_pages}
    missing = expected - listed
    log(f"  /topics/ hub lists {len(listed)} tags, expected {len(expected)} tag pages")
    if missing: log(f"  MISSING from /topics/ hub: {sorted(missing)}")
    return {"missing": sorted(missing), "listed": len(listed), "expected": len(expected)}


def audit_tag_pages(tag_pages):
    log("Auditing each /topics/<slug>/ for empty state...")
    empty = []
    for tp in tag_pages:
        html = fetch_url_html(f"{SITE}/topics/{tp['slug']}/")
        if "post-card" not in html:
            empty.append(tp["slug"])
    log(f"  Empty tag pages: {len(empty)}")
    if empty: log(f"  EMPTY: {sorted(empty)}")
    return {"empty_tag_pages": sorted(empty)}


def audit_category_archives():
    log("Auditing category archive pages...")
    results = {}
    for label, path in CATEGORY_PAGES:
        html = fetch_url_html(f"{SITE}{path}")
        count = len(re.findall(r'class="post-card"', html))
        results[path] = {"label": label, "post_count": count}
        log(f"  {path} -> {count} cards")
    return results


def audit_homepage_carousel(blog_post_pages):
    log("Auditing homepage carousel...")
    home_html = fetch_page_html(HOMEPAGE_ID)
    listed = set(re.findall(r'<a href="/([a-z0-9\-]+)/" class="tc-card"', home_html))
    cutoff = (dt.datetime.now() - dt.timedelta(days=30)).isoformat()
    recent = [p for p in blog_post_pages if p.get("date", "") >= cutoff]
    recent_slugs = {p["slug"] for p in recent}
    missing = recent_slugs - listed
    log(f"  Homepage carousel: {len(listed)} cards, {len(recent_slugs)} recent posts (last 30 days)")
    if missing: log(f"  MISSING recent from carousel: {sorted(missing)}")
    return {"listed": len(listed), "recent_count": len(recent_slugs), "missing_recent": sorted(missing)}


def telegram_notify(text: str):
    if not TG_BOT or not TG_CHAT:
        log("  TG secrets missing — skipping notification")
        return
    url = f"https://api.telegram.org/bot{TG_BOT}/sendMessage"
    data = parse.urlencode({"chat_id": TG_CHAT, "text": text, "parse_mode": "Markdown"}).encode()
    try:
        with request.urlopen(request.Request(url, data=data), timeout=20) as r:
            r.read()
        log("  Telegram notification sent")
    except Exception as e:
        log(f"  TG send ERR: {e}")


def main():
    json_mode = "--json" in sys.argv
    log("=" * 60)
    log("Bi-weekly content sync audit starting...")

    if not USER or not PASS:
        log("FAIL: WORDPRESS_USERNAME / WORDPRESS_PASSWORD env vars not set")
        sys.exit(1)

    log("Fetching all WP pages...")
    all_pages = list_all_pages()
    log(f"  Total pages: {len(all_pages)}")

    tag_pages = [p for p in all_pages if p.get("parent") == TOPICS_HUB_ID and p.get("status") == "publish"]
    log(f"  Tag pages under /topics/: {len(tag_pages)}")

    blog_post_pages = [
        p for p in all_pages
        if p.get("parent") == 0
        and p.get("status") == "publish"
        and (
            "-singapore" in p.get("slug", "")
            or any(p.get("slug", "").startswith(prefix) for prefix in [
                "coe-", "scrap-", "first-car-", "how-often-", "tyres-",
                "dashboard-", "10-signs", "what-to-look", "block-exemption",
                "12-questions", "dealer-vs", "how-to-read-", "what-is-the-right-workshop",
                "erp-",
            ])
        )
        and not p.get("slug", "").startswith("topics-")
        and "results" not in p.get("slug", "")
    ]
    log(f"  Blog posts (heuristic): {len(blog_post_pages)}")

    report = {
        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "blog_index":         audit_blog_index(blog_post_pages),
        "topics_hub":         audit_topics_hub(tag_pages),
        "tag_pages":          audit_tag_pages(tag_pages),
        "category_archives":  audit_category_archives(),
        "homepage_carousel":  audit_homepage_carousel(blog_post_pages),
    }

    issues = (
        len(report["blog_index"]["missing"])
        + len(report["topics_hub"]["missing"])
        + len(report["tag_pages"]["empty_tag_pages"])
        + len(report["homepage_carousel"]["missing_recent"])
    )

    log("")
    log(f"TOTAL ISSUES: {issues}")
    if issues == 0:
        log("✓ All content sync checks pass.")
        # Also notify on green so Ed knows it's running
        telegram_notify(
            f"✅ TRW Bi-weekly Content Sync ({dt.date.today().isoformat()})\n\n"
            f"All checks passed.\n"
            f"• /blog/: {report['blog_index']['listed']} cards\n"
            f"• /topics/: {report['topics_hub']['listed']} tags\n"
            f"• Tag pages: {report['topics_hub']['listed']} (no empty)\n"
            f"• Categories: Guides {report['category_archives']['/guides/']['post_count']}, "
            f"Car Tips {report['category_archives']['/car-tips/']['post_count']}, "
            f"News {report['category_archives']['/news/']['post_count']}"
        )
    else:
        log("⚠ Drift detected — manual fix needed:")
        msg_lines = [f"⚠ TRW Content Sync Drift ({dt.date.today().isoformat()}) — {issues} issue(s):\n"]
        if report["blog_index"]["missing"]:
            msg_lines.append(f"*Missing from /blog/:* {', '.join(report['blog_index']['missing'])}")
        if report["topics_hub"]["missing"]:
            msg_lines.append(f"*Missing from /topics/ hub:* {', '.join(report['topics_hub']['missing'])}")
        if report["tag_pages"]["empty_tag_pages"]:
            msg_lines.append(f"*Empty tag pages:* {', '.join(report['tag_pages']['empty_tag_pages'])}")
        if report["homepage_carousel"]["missing_recent"]:
            msg_lines.append(f"*Missing recent from homepage:* {', '.join(report['homepage_carousel']['missing_recent'])}")
        msg_lines.append("\nFix via: edit push_tag_pages.py / add_blog_cards_batch.py and re-run.")
        telegram_notify("\n".join(msg_lines))

    if json_mode:
        print(json.dumps(report, indent=2))

    # Always exit 0 so the workflow doesn't fail on drift (drift is normal,
    # we just want to surface it via Telegram).
    sys.exit(0)


if __name__ == "__main__":
    main()
