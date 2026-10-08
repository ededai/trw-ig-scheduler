#!/usr/bin/env python3
"""Publish a prepared /news/ article bundle to WordPress.

A bundle is a folder with:
  article.json        slug, title, meta_description, tags, featured_image
  publish/page.html   final page HTML (Cole's render_news_post output), with
                      {{IMG:<file>}} placeholders for every image
  featured.png, infographics/*.png

Mirrors cole.wp_publisher.WordPressClient.upsert_page for news articles:
top-level page, elementor_canvas template, wp:html block, rank_math
description, excerpt, featured_media, _trw_canonical_chrome and the
_trw_is_article/_trw_cat meta that put the page on /blog/, /news/ and the
/topics/ grids. Idempotent by slug: a re-run updates the same page.

Usage: python3 tools/publish_prepared_article.py <bundle-dir> [--status publish|draft]
Env:   WORDPRESS_API_URL, WORDPRESS_USERNAME, WORDPRESS_PASSWORD
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path

import requests

MIN_PAGE_CHARS = 2_000


def wp_base() -> str:
    url = os.environ["WORDPRESS_API_URL"].strip().rstrip("/")
    if not url.endswith("/wp/v2"):
        url = url.rstrip("/") + ("/wp/v2" if url.endswith("/wp-json") else "/wp-json/wp/v2")
    return url


def headers() -> dict:
    user = os.environ["WORDPRESS_USERNAME"].strip()
    pw = os.environ["WORDPRESS_PASSWORD"].strip()
    token = base64.b64encode(f"{user}:{pw}".encode()).decode()
    return {"Authorization": f"Basic {token}", "Accept": "application/json"}


def req(method: str, path: str, **kw):
    r = requests.request(method, wp_base() + path, headers=headers(), timeout=120, **kw)
    if not r.ok:
        print(f"::error::WP {method} {path} -> {r.status_code} {r.text[:400]}")
    r.raise_for_status()
    return r.json() if r.content else {}


def upload(path: Path, alt: str) -> dict:
    h = headers()
    h["Content-Type"] = "image/png"
    h["Content-Disposition"] = f'attachment; filename="{path.name}"'
    r = requests.post(wp_base() + "/media", headers=h, data=path.read_bytes(), timeout=180)
    if not r.ok:
        print(f"::error::upload {path.name} -> {r.status_code} {r.text[:400]}")
    r.raise_for_status()
    media = r.json()
    try:
        req("POST", f"/media/{media['id']}", json={"alt_text": alt})
    except Exception as e:  # alt text is best-effort, like Cole
        print(f"::warning::alt text for {path.name} failed: {e}")
    print(f"uploaded {path.name} -> id={media['id']} {media['source_url']}")
    return media


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle")
    ap.add_argument("--status", default="publish", choices=["publish", "draft"])
    args = ap.parse_args()

    root = Path(args.bundle)
    meta = json.loads((root / "article.json").read_text())
    html = (root / "publish" / "page.html").read_text()
    slug, title = meta["slug"], meta["title"]

    existing = req("GET", f"/pages?slug={slug}&status=publish,draft&_fields=id,featured_media,link")

    alts = {
        "featured.png": title,
        "coe-merger-infographic-1": "Two COE queues become one: today Cat A and Cat B bid separately; under LTA's proposal all cars bid together, then get a rebate or surcharge based on the car's value",
        "coe-merger-infographic-3": "Same COE, different final bill: example of what buyers in each band would pay under LTA's three-band and five-band options",
        "coe-merger-infographic-4": "What happens next: consultation opens 8 October 2026, feedback closes 2 November 2026, LTA decision in the first half of 2027",
        "coe-merger-infographic-5": "How bands would be set: median OMV per model, ranked and split by percentile; engine size no longer sorts cars",
    }

    names = sorted(set(re.findall(r"\{\{IMG:([^}]+)\}\}", html)))
    urls, featured_id = {}, None
    # Re-runs reuse the media from the previous publish instead of uploading duplicates.
    prev_path = root / "publish" / "result.json"
    if prev_path.exists():
        prev = json.loads(prev_path.read_text())
        urls = {k: v for k, v in (prev.get("media") or {}).items() if k in names}
        featured_id = prev.get("featured_media") if "featured.png" in urls else None
        if urls:
            print(f"reusing {len(urls)} previously uploaded image(s)")
    for name in names:
        if name in urls:
            continue
        p = root / name if name == "featured.png" else root / "infographics" / name
        alt = alts.get(name) or alts.get(name.replace("-mobile.png", "").replace(".png", ""), title)
        media = upload(p, alt)
        urls[name] = media["source_url"]
        if name == "featured.png":
            featured_id = media["id"]
    for name, url in urls.items():
        html = html.replace("{{IMG:" + name + "}}", url)
    left = re.findall(r"\{\{IMG:[^}]+\}\}", html)
    if left:
        print(f"::error::unresolved image placeholders: {left}")
        return 1
    if len(html) < MIN_PAGE_CHARS:
        print("::error::page HTML suspiciously short, refusing to publish")
        return 1

    body = {
        "slug": slug,
        "title": title,
        "content": f"<!-- wp:html -->\n{html}\n<!-- /wp:html -->",
        "status": args.status,
        "template": "elementor_canvas",
        "excerpt": meta["meta_description"],
        "meta": {
            "rank_math_description": meta["meta_description"],
            "_trw_canonical_chrome": "yes",
            "_trw_is_article": "1",
            "_trw_cat": "News",
        },
    }
    if featured_id:
        body["featured_media"] = featured_id

    if existing:
        page = req("POST", f"/pages/{existing[0]['id']}", json=body)
        print(f"updated page id={page['id']}")
    else:
        page = req("POST", "/pages", json=body)
        print(f"created page id={page['id']}")

    link = page.get("link")
    print(f"::notice::Live URL: {link}")
    out = {"page_id": page["id"], "link": link, "status": page.get("status"),
           "featured_media": featured_id, "media": urls}
    (root / "publish" / "result.json").write_text(json.dumps(out, indent=2))
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a") as fh:
            fh.write(f"link={link}\npage_id={page['id']}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
