#!/usr/bin/env python3
"""
Fix og:image + schema.org Article image drift across all TRW blog articles.

Root cause: WP blog pages had no `featured_media` set (or had stale ones), so
RankMath/Yoast fell back to the site logo for og:image and produced a schema
Article image that was unrelated to the actual article hero.

Fix: for each blog article, derive the canonical hero from its live
<section class="article-hero"> img, look up the matching WP media item,
and set `featured_media` on the article's WP page. og:image and
schema.org Article image are both derived from featured_media, so both
become correct after one REST call per page.

This script is the SINGLE source of truth for the article-image drift fix.
Do NOT copy-paste its logic into other scripts.

Modes:
  --check    Dry-run. Prints each page's current vs. target featured_media.
  --apply    Apply changes.

Reuses helpers from refresh_trw_blog_index (single source of truth).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib import request, error

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

from refresh_trw_blog_index import (  # type: ignore
    load_env,
    load_config,
    wp_base,
    auth_header,
    http_get,
    http_post_json,
    fetch_blog_page_raw,
    unwrap_wp_html,
    parse_cards,
    extract_article_hero_src,
    extract_og_image,
    extract_schema_article_image,
    clean_src,
    log,
)

from bs4 import BeautifulSoup


# ---------- WP lookups ----------

def wp_find_page_by_slug(env: dict, slug: str) -> dict | None:
    base = wp_base(env)
    url = f"{base}/wp-json/wp/v2/pages?slug={slug}&context=edit&per_page=5"
    headers = {"Authorization": auth_header(env), "User-Agent": "trw-fix-feat/1.0"}
    req = request.Request(url, headers=headers)
    with request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data[0] if data else None


def wp_find_media_by_filename(env: dict, filename: str) -> dict | None:
    """Search media library for an item whose source_url ends with this filename."""
    base = wp_base(env)
    # Strip extension and v-suffix to broaden search, then filter client-side
    stem = Path(filename).stem
    url = f"{base}/wp-json/wp/v2/media?search={stem}&context=edit&per_page=20"
    headers = {"Authorization": auth_header(env), "User-Agent": "trw-fix-feat/1.0"}
    req = request.Request(url, headers=headers)
    with request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    # Match exact filename
    for item in data:
        src = item.get("source_url", "")
        if src.endswith("/" + filename):
            return item
    # Fallback: match stem
    for item in data:
        src = item.get("source_url", "")
        if stem in src:
            return item
    return None


def wp_set_featured_media(env: dict, page_id: int, media_id: int) -> dict:
    base = wp_base(env)
    url = f"{base}/wp-json/wp/v2/pages/{page_id}"
    headers = {
        "Authorization": auth_header(env),
        "Content-Type": "application/json",
        "User-Agent": "trw-fix-feat/1.0",
    }
    return http_post_json(url, {"featured_media": media_id}, headers)


# ---------- main ----------

def run(mode: str) -> int:
    env = load_env()
    cfg = load_config()
    page_id = cfg["blog_page_id"]
    origin = cfg["site_origin"]

    # Pull the 17 cards from live /blog/ (single source of truth)
    page = fetch_blog_page_raw(env, page_id)
    raw = page["content"]["raw"]
    inner, _ = unwrap_wp_html(raw)
    soup = BeautifulSoup(inner, "lxml")
    cards = parse_cards(soup)

    print("=" * 72)
    print(f"ARTICLE FEATURED IMAGE FIX  |  mode={mode}  |  {len(cards)} articles")
    print("=" * 72)

    pending = []
    errors = []

    for c in cards:
        slug = c["slug"]
        url = c["href"]
        if not url.startswith("http"):
            url = origin.rstrip("/") + url
        try:
            html = http_get(url)
        except Exception as e:
            errors.append((slug, f"fetch article: {e}"))
            continue

        hero = extract_article_hero_src(html)
        if not hero:
            errors.append((slug, "no article-hero img found"))
            continue
        hero_clean = clean_src(hero)
        filename = hero_clean.rsplit("/", 1)[-1]

        wp_page = wp_find_page_by_slug(env, slug)
        if not wp_page:
            errors.append((slug, "wp page not found"))
            continue
        current_fm = wp_page.get("featured_media", 0)

        media = wp_find_media_by_filename(env, filename)
        if not media:
            errors.append((slug, f"media not found: {filename}"))
            continue
        target_fm = media["id"]

        og = clean_src(extract_og_image(html) or "")
        schema = clean_src(extract_schema_article_image(html) or "")

        row = {
            "slug": slug,
            "page_id": wp_page["id"],
            "current_featured_media": current_fm,
            "target_featured_media": target_fm,
            "target_filename": filename,
            "og_before": og,
            "schema_before": schema,
        }
        needs_change = current_fm != target_fm
        row["needs_change"] = needs_change
        pending.append(row)

        tag = "CHANGE" if needs_change else "ok    "
        print(f"  [{tag}] {slug}")
        print(f"           page_id={wp_page['id']}  featured_media: {current_fm} -> {target_fm}  ({filename})")

    changes = [r for r in pending if r["needs_change"]]
    print(f"\n{len(changes)} of {len(pending)} articles need featured_media update. Errors: {len(errors)}")
    for slug, err in errors:
        print(f"  ERROR {slug}: {err}")

    if mode == "check":
        return 0 if not errors else 1

    if not changes:
        print("No-op.")
        return 0

    for row in changes:
        try:
            resp = wp_set_featured_media(env, row["page_id"], row["target_featured_media"])
            log(
                f"featured_media fix: {row['slug']} page={row['page_id']} "
                f"{row['current_featured_media']} -> {row['target_featured_media']}"
            )
            print(f"  applied {row['slug']}  modified={resp.get('modified')}")
        except Exception as e:
            print(f"  FAIL {row['slug']}: {e}")
            errors.append((row["slug"], f"apply: {e}"))

    # Post-check: re-fetch a few articles and confirm og:image
    print("\nPost-fix spot-check (3 samples, allow 10s propagation)...")
    time.sleep(10)
    sample = changes[:3]
    for row in sample:
        try:
            html = http_get(f"{origin}/{row['slug']}/")
            og_after = clean_src(extract_og_image(html) or "")
            schema_after = clean_src(extract_schema_article_image(html) or "")
            ok_og = row["target_filename"] in og_after
            ok_sch = row["target_filename"] in schema_after
            print(f"  {row['slug']}: og {'✓' if ok_og else 'drift still'}={og_after}  |  schema {'✓' if ok_sch else 'drift still'}={schema_after}")
        except Exception as e:
            print(f"  {row['slug']}: post-check fail {e}")
    return 0 if not errors else 1


def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--apply", action="store_true")
    args = p.parse_args()
    sys.exit(run("check" if args.check else "apply"))


if __name__ == "__main__":
    main()
