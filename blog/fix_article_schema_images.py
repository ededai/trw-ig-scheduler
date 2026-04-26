#!/usr/bin/env python3
"""
Fix schema.org Article image drift across all TRW blog articles.

Root cause: each article's wp:html block contains a hardcoded
<script type="application/ld+json"> with @type=Article (or BlogPosting)
whose `image` field was copy-pasted from a template and left pointing
at the WRONG hero (e.g. first-service article advertised tyre_treadgauge
to Google). Setting featured_media does NOT fix this — the JSON-LD is
literal text inside the page body.

This script rewrites the `image` field in every Article / BlogPosting
JSON-LD script tag on each blog page, using the canonical hero URL from
that page's own <section class="article-hero"> img src.

Single source of truth: the live article hero. Never a mockup file.
Never a hardcoded dict.

Safety:
- Uses bs4 for HTML parse (preserves <style>, <script> bodies, wp:html wrap).
- Only modifies the `.string` of <script type="application/ld+json"> tags.
- Skips articles whose schema is already correct (idempotent).
- Preserves other JSON-LD scripts (FAQPage etc.) unchanged.

Modes:
  --check    Print current vs. target image per article, no writes.
  --apply    Apply fixes + verify.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib import request

from bs4 import BeautifulSoup

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

from refresh_trw_blog_index import (  # type: ignore
    load_env, load_config, wp_base, auth_header,
    http_get, http_post_json,
    fetch_blog_page_raw, unwrap_wp_html, rewrap_wp_html,
    parse_cards, extract_article_hero_src, clean_src, log,
)


def fetch_page(env: dict, pid: int) -> dict:
    base = wp_base(env)
    req = request.Request(
        f"{base}/wp-json/wp/v2/pages/{pid}?context=edit",
        headers={"Authorization": auth_header(env), "User-Agent": "trw-schema/1.0"},
    )
    with request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def push_page_content(env: dict, pid: int, new_content: str) -> dict:
    base = wp_base(env)
    url = f"{base}/wp-json/wp/v2/pages/{pid}"
    headers = {
        "Authorization": auth_header(env),
        "Content-Type": "application/json",
        "User-Agent": "trw-schema/1.0",
    }
    return http_post_json(url, {"content": new_content}, headers)


def find_wp_page_by_slug(env: dict, slug: str) -> dict | None:
    base = wp_base(env)
    url = f"{base}/wp-json/wp/v2/pages?slug={slug}&context=edit&per_page=3"
    req = request.Request(
        url, headers={"Authorization": auth_header(env), "User-Agent": "trw-schema/1.0"}
    )
    with request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    return data[0] if data else None


def update_article_schemas(inner_html: str, correct_image_url: str) -> tuple[str, list[dict]]:
    """Rewrite `image` field in Article/BlogPosting JSON-LD scripts within the page body.

    Returns (new_inner_html, list_of_changes).
    Changes = [{'schema_type', 'from', 'to'}, ...]
    """
    soup = BeautifulSoup(inner_html, "lxml")
    changes = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        text = script.string
        if not text:
            continue
        stripped = text.strip()
        try:
            data = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        mutated = False

        def walk(o):
            nonlocal mutated
            if isinstance(o, dict):
                t = o.get("@type")
                if t in ("Article", "BlogPosting", "NewsArticle"):
                    cur = o.get("image")
                    # Normalise for comparison
                    cur_str = cur if isinstance(cur, str) else (cur or {}).get("url") if isinstance(cur, dict) else ""
                    if cur_str != correct_image_url:
                        changes.append({
                            "schema_type": t,
                            "from": cur_str or "(empty)",
                            "to": correct_image_url,
                        })
                        o["image"] = correct_image_url
                        mutated = True
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)

        walk(data)
        if mutated:
            new_json = json.dumps(data, ensure_ascii=False)
            script.string = new_json

    if not changes:
        return inner_html, []
    # Strip the html/body wrap lxml adds
    out = soup.decode()
    out = re.sub(r"^\s*<html><body>", "", out)
    out = re.sub(r"</body></html>\s*$", "", out)
    return out, changes


def run(mode: str) -> int:
    env = load_env()
    cfg = load_config()
    page_id = cfg["blog_page_id"]
    origin = cfg["site_origin"]

    page = fetch_blog_page_raw(env, page_id)
    inner, _ = unwrap_wp_html(page["content"]["raw"])
    soup = BeautifulSoup(inner, "lxml")
    cards = parse_cards(soup)

    print("=" * 72)
    print(f"ARTICLE SCHEMA IMAGE FIX  |  mode={mode}  |  {len(cards)} articles")
    print("=" * 72)

    pending = []
    for c in cards:
        slug = c["slug"]
        try:
            live = http_get(f"{origin}/{slug}/")
        except Exception as e:
            print(f"  FETCH_FAIL {slug}: {e}")
            continue
        hero = extract_article_hero_src(live)
        if not hero:
            print(f"  NO_HERO {slug}")
            continue
        correct = clean_src(hero)

        wp_page = find_wp_page_by_slug(env, slug)
        if not wp_page:
            print(f"  NO_WP_PAGE {slug}")
            continue
        pid = wp_page["id"]

        full = fetch_page(env, pid)
        raw_content = full["content"]["raw"]
        inner_content, was_wrapped = unwrap_wp_html(raw_content)
        new_inner, changes = update_article_schemas(inner_content, correct)
        pending.append({
            "slug": slug,
            "page_id": pid,
            "correct_hero": correct,
            "changes": changes,
            "new_inner": new_inner,
            "was_wrapped": was_wrapped,
        })
        if changes:
            print(f"  CHANGE {slug}  page_id={pid}")
            for ch in changes:
                print(f"    {ch['schema_type']}.image:")
                print(f"      from: {ch['from'][:90]}")
                print(f"      to  : {ch['to'][:90]}")
        else:
            print(f"  ok     {slug}")

    changing = [r for r in pending if r["changes"]]
    print(f"\n{len(changing)} of {len(pending)} articles need schema fix.")

    if mode == "check":
        return 0

    if not changing:
        print("No-op.")
        return 0

    for row in changing:
        new_content = rewrap_wp_html(row["new_inner"], row["was_wrapped"])
        try:
            resp = push_page_content(env, row["page_id"], new_content)
            log(f"schema fix: {row['slug']} page={row['page_id']} image->{row['correct_hero']}")
            print(f"  pushed {row['slug']}  modified={resp.get('modified')}")
        except Exception as e:
            print(f"  FAIL {row['slug']}: {e}")

    # Verify
    print("\nWaiting 10s then verifying...")
    time.sleep(10)
    from refresh_trw_blog_index import extract_schema_article_image
    ok = fail = 0
    for row in changing:
        html = http_get(f"{origin}/{row['slug']}/")
        sch = clean_src(extract_schema_article_image(html) or "")
        hero_stem = row["correct_hero"].rsplit("/", 1)[-1].rsplit(".", 1)[0]
        good = hero_stem in sch
        ok += good
        fail += (not good)
        print(f"  {'✓' if good else '✗'} {row['slug']}  schema={sch}")
    print(f"\nschema correct after push: {ok}/{ok+fail}")
    return 0 if fail == 0 else 1


def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--apply", action="store_true")
    args = p.parse_args()
    sys.exit(run("check" if args.check else "apply"))


if __name__ == "__main__":
    main()
