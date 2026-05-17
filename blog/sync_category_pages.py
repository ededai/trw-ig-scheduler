#!/usr/bin/env python3
"""Add-only daily sync for /guides/, /car-tips/, /news/ category hub pages.

Cron-friendly counterpart to wp-import/push_category_pages.py (which is a
full rebuild — destructive, requires the wp-import repo).

This script:
  1. Queries WP REST for all published pages in each category (Guides /
     Car Tips / News) via the WP `categories` taxonomy.
  2. For each of the 3 hub pages (/guides/=1772, /car-tips/=1774,
     /news/=1776), reads raw content, finds the existing post-card slugs,
     identifies WP-discovered slugs that are missing.
  3. Builds + injects a card for each missing slug, mirroring sync_blog_hub_posts.py's pattern (featured_media first, article-hero img fallback).
  4. Pushes updated hub content back to WP.

Idempotent: re-runs are no-ops once everything is in sync.
"""
from __future__ import annotations
import base64, html as html_mod, json, os, re, sys
from pathlib import Path
from urllib import request, error

WP_ORIGIN = "https://therightworkshop.com"
HUB_BY_CAT = {
    "Guides":   1772,
    "Car Tips": 1774,
    "News":     1776,
}
CAT_TO_WP_SLUG = {"Guides": "guides", "Car Tips": "car-tips", "News": "news"}
HERE = Path(__file__).parent


def load_env() -> dict:
    env = {}
    for k in ("WORDPRESS_USERNAME", "WORDPRESS_PASSWORD", "WORDPRESS_API_URL"):
        if os.environ.get(k):
            env[k] = os.environ[k]
    if len(env) == 3:
        return env
    for cand in [
        Path("/Users/admin/the-right-workshop/tools/.env"),
        HERE.parent / "tools" / ".env",
        Path(".env"),
    ]:
        if cand.exists():
            for line in cand.read_text().splitlines():
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            break
    return env


def auth_header(env: dict) -> str:
    return "Basic " + base64.b64encode(
        f"{env['WORDPRESS_USERNAME']}:{env['WORDPRESS_PASSWORD']}".encode()
    ).decode()


def wp_get(env: dict, path: str, params: str = ""):
    url = f"{WP_ORIGIN}/wp-json/wp/v2{path}{params}"
    req = request.Request(url, headers={"Authorization": auth_header(env)})
    try:
        with request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except error.HTTPError as e:
        print(f"  GET {path} -> HTTP {e.code}: {e.read().decode()[:200]}")
        return None


def wp_push(env: dict, page_id: int, content: str) -> bool:
    url = f"{WP_ORIGIN}/wp-json/wp/v2/pages/{page_id}"
    body = json.dumps({"content": content}).encode()
    req = request.Request(
        url, data=body, method="POST",
        headers={"Authorization": auth_header(env), "Content-Type": "application/json"},
    )
    try:
        with request.urlopen(req, timeout=60) as r:
            r.read()
            return True
    except error.HTTPError as e:
        print(f"  POST {page_id} -> HTTP {e.code}: {e.read().decode()[:200]}")
        return False


def strip_html(s: str) -> str:
    if not s: return ''
    return html_mod.unescape(re.sub(r'<[^>]+>', '', s)).strip()


def discover_articles_by_category(env: dict) -> dict[str, list[dict]]:
    """Return {cat_name: [{id,slug,title,excerpt,featured_media}, ...]}."""
    cats = wp_get(env, "/categories", "?per_page=100&_fields=id,slug") or []
    by_slug = {c["slug"]: c["id"] for c in cats}
    out: dict[str, list[dict]] = {}
    for cat_name, wp_slug in CAT_TO_WP_SLUG.items():
        cat_id = by_slug.get(wp_slug)
        if not cat_id:
            print(f"  WARN: WP category '{wp_slug}' not found")
            out[cat_name] = []
            continue
        pages = wp_get(
            env, "/pages",
            f"?categories={cat_id}&per_page=100&status=publish&orderby=date&order=desc"
            f"&_fields=id,slug,title,excerpt,featured_media",
        ) or []
        out[cat_name] = pages
    return out


def resolve_hero(env: dict, page_id: int, featured_media_id: int) -> tuple[str, str]:
    """featured_media first, article-hero img fallback."""
    if featured_media_id:
        m = wp_get(env, f"/media/{featured_media_id}", "?_fields=source_url,alt_text")
        if m and m.get("source_url"):
            src = re.sub(r'^https?://i\d+\.wp\.com/', 'https://', m["source_url"]).split('?')[0]
            return (src, m.get("alt_text") or "")
    data = wp_get(env, f"/pages/{page_id}", "?context=edit&_fields=content")
    if data:
        content = (data.get("content") or {}).get("raw", "") or ""
        m = re.search(
            r'<section class="article-hero">.*?<img[^>]*src="([^"]+)"[^>]*alt="([^"]*)"',
            content, re.S,
        )
        if m:
            src = re.sub(r'^https?://i\d+\.wp\.com/', 'https://', m.group(1)).split('?')[0]
            return (src, m.group(2))
    return ("", "")


def build_card(slug: str, cat_name: str, title: str, excerpt: str,
               hero_src: str, hero_alt: str) -> str:
    return (
        f'<a class="post-card" data-cat="{cat_name}" href="/{slug}/">'
        f'<div class="pc-media"><img src="{hero_src}" alt="{hero_alt}" data-recalc-dims="1" decoding="async"></div>'
        f'<div class="pc-body"><div class="pc-eyebrow">{cat_name}</div>'
        f'<h3>{title}</h3>'
        f'<p>{excerpt[:200]}</p>'
        f'<div class="pc-meta">By The Right Workshop team</div></div></a>'
    )


def extract_existing_slugs(raw: str) -> set[str]:
    return set(re.findall(r'class="post-card"[^>]*href="/([^"/]+)/"', raw))


def inject_into_grid(raw: str, card_html: str) -> tuple[str, bool]:
    """Insert card just before the closing </div> of <div class='post-grid'...>.
    Returns (new_raw, success)."""
    m = re.search(r'<div\s+class="post-grid"[^>]*>', raw)
    if not m:
        return raw, False
    open_end = m.end()
    depth = 1
    pos = open_end
    div_re = re.compile(r'</?div\b', re.IGNORECASE)
    while pos < len(raw):
        mm = div_re.search(raw, pos)
        if not mm:
            return raw, False
        if raw[mm.start():mm.start() + 2] == "</":
            depth -= 1
            if depth == 0:
                close_start = mm.start()
                return raw[:close_start] + "\n      " + card_html + raw[close_start:], True
            pos = mm.end()
        else:
            depth += 1
            pos = mm.end()
    return raw, False


def main() -> int:
    env = load_env()
    if not env.get("WORDPRESS_USERNAME"):
        print("ABORT: WP credentials missing")
        return 1
    print("sync_category_pages: discovering articles by WP category...")
    by_cat = discover_articles_by_category(env)
    total_added = 0
    for cat_name, hub_pid in HUB_BY_CAT.items():
        articles = by_cat.get(cat_name, [])
        if not articles:
            print(f"  /{CAT_TO_WP_SLUG[cat_name]}/: no articles in WP category, skipping")
            continue
        hub_page = wp_get(env, f"/pages/{hub_pid}", "?context=edit&_fields=content")
        if not hub_page:
            print(f"  /{CAT_TO_WP_SLUG[cat_name]}/: failed to fetch hub page {hub_pid}")
            continue
        raw = (hub_page.get("content") or {}).get("raw", "") or ""
        existing = extract_existing_slugs(raw)
        missing = [a for a in articles if a["slug"] not in existing]
        if not missing:
            print(f"  /{CAT_TO_WP_SLUG[cat_name]}/ ({hub_pid}): up-to-date ({len(existing)} cards)")
            continue
        print(f"  /{CAT_TO_WP_SLUG[cat_name]}/ ({hub_pid}): adding {len(missing)} card(s)")
        new_raw = raw
        for a in missing:
            slug = a["slug"]
            title = strip_html((a.get("title") or {}).get("rendered", slug))
            excerpt = strip_html((a.get("excerpt") or {}).get("rendered", ""))
            hero_src, hero_alt = resolve_hero(env, a["id"], a.get("featured_media") or 0)
            if not hero_src:
                print(f"      ! /{slug}/ no hero — skipping")
                continue
            card = build_card(slug, cat_name, title, excerpt, hero_src, hero_alt or title)
            new_raw, ok = inject_into_grid(new_raw, card)
            if ok:
                print(f"      + /{slug}/ added")
                total_added += 1
            else:
                print(f"      ! /{slug}/ inject failed (no .post-grid found)")
        if new_raw != raw:
            if wp_push(env, hub_pid, new_raw):
                print(f"      pushed.")
            else:
                print(f"      push FAILED.")
    print(f"\nTotal cards added: {total_added}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
