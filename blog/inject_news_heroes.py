#!/usr/bin/env python3
"""inject_news_heroes.py — inject <section class="article-hero"> into news articles
that have featured_media set in WP but were built with an older template that has
no article-hero section in the HTML.

Targets:
  page 6279  media 6829  (ERP OBU)
  page 6199  media 6835  (VEP GVP Fees)
  page 6193  media 6840  (EV Plates / LTA)
  page 6187  media 6845  (PARF Rebate)

Usage:
  python3 inject_news_heroes.py --dry-run
  python3 inject_news_heroes.py
"""
from __future__ import annotations
import argparse, base64, json, re, sys
from pathlib import Path
from urllib import request, error

WP_ORIGIN = "https://therightworkshop.com"
HERE = Path(__file__).parent

TARGETS = [
    {"page_id": 6279, "media_id": 6829, "label": "ERP OBU",      "alt_fallback": "Singapore ERP On-Board Unit mounted on a car windscreen"},
    {"page_id": 6199, "media_id": 6835, "label": "VEP GVP Fees", "alt_fallback": "Singapore Vehicle Entry Permit and Green Vehicle Pass fees guide"},
    {"page_id": 6193, "media_id": 6840, "label": "EV Plates",    "alt_fallback": "LTA electric vehicle green number plates in Singapore"},
    {"page_id": 6187, "media_id": 6845, "label": "PARF Rebate",  "alt_fallback": "Singapore PARF rebate and COE rebate guide"},
]

HERO_TEMPLATE = (
    '<section class="article-hero">'
    '<div class="wrapper"><div class="hero-wrap">'
    '<img data-recalc-dims="1" loading="lazy" decoding="async" src="{src}" alt="{alt}">'
    '</div></div></section>'
)

def load_env() -> dict:
    env = {}
    for candidate in [
        Path("/Users/admin/the-right-workshop/tools/.env"),
        HERE.parent / "tools" / ".env",
        Path(".env"),
    ]:
        if candidate.exists():
            for line in candidate.read_text().splitlines():
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    v = v.strip().strip('"').strip("'")
                    env.setdefault(k.strip(), v)
            break
    return env

def auth_header(env):
    creds = f"{env['WORDPRESS_USERNAME']}:{env['WORDPRESS_PASSWORD']}"
    return {"Authorization": "Basic " + base64.b64encode(creds.encode()).decode()}

def wp_get(env, path, query=""):
    url = f"{WP_ORIGIN}/wp-json/wp/v2{path}{query}"
    req = request.Request(url, headers=auth_header(env))
    with request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())

def wp_patch(env, path, payload):
    url = f"{WP_ORIGIN}/wp-json/wp/v2{path}"
    data = json.dumps(payload).encode()
    headers = {**auth_header(env), "Content-Type": "application/json"}
    req = request.Request(url, data=data, headers=headers, method="PATCH")
    try:
        with request.urlopen(req, timeout=30) as r:
            return r.status in (200, 201)
    except error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.read().decode()[:300]}")
        return False

def fetch_media(env, media_id):
    try:
        m = wp_get(env, f"/media/{media_id}", "?_fields=source_url,alt_text")
        src = m.get("source_url", "")
        # Strip Jetpack proxy prefix to get clean URL
        src = re.sub(r'^https?://i\d+\.wp\.com/', 'https://', src).split("?")[0]
        alt = m.get("alt_text", "") or ""
        return src, alt
    except Exception as e:
        print(f"  ! fetch_media({media_id}): {e}")
        return None, None

def inject_hero(raw: str, hero_html: str) -> tuple[str, bool]:
    """Insert hero section after the closing </section> of the article-head block.

    Pattern: <section class="article-head">...</section> followed by whatever comes next.
    We inject hero between the </section> of article-head and the next element.
    """
    # Find article-head section's closing </section>
    head_open = re.search(r'<section[^>]*class="[^"]*article-head[^"]*"', raw)
    if not head_open:
        print("  ! article-head section not found")
        return raw, False

    # Find the matching </section> using depth counting
    start = head_open.end()
    depth = 1
    i = start
    open_re = re.compile(r'<section\b', re.IGNORECASE)
    close_re = re.compile(r'</section\s*>', re.IGNORECASE)

    while i < len(raw) and depth > 0:
        om = open_re.search(raw, i)
        cm = close_re.search(raw, i)
        if not cm:
            break
        if om and om.start() < cm.start():
            depth += 1
            i = om.end()
        else:
            depth -= 1
            if depth == 0:
                # cm.end() is right after </section>
                inject_pos = cm.end()
                new_raw = raw[:inject_pos] + hero_html + raw[inject_pos:]
                return new_raw, True
            i = cm.end()

    print("  ! could not find closing </section> of article-head")
    return raw, False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    env = load_env()
    if not env.get("WORDPRESS_USERNAME"):
        sys.exit("ERROR: WP credentials missing")

    for t in TARGETS:
        print(f"\n{'='*50}")
        print(f"Processing: {t['label']} (page {t['page_id']}, media {t['media_id']})")

        # Fetch media
        src, alt = fetch_media(env, t["media_id"])
        if not src:
            print("  ✗ could not fetch media — skipping")
            continue
        if not alt:
            alt = t.get("alt_fallback", "")
        print(f"  Media src: {src}")
        print(f"  Media alt: {alt!r}")

        # Fetch page raw content
        try:
            page = wp_get(env, f"/pages/{t['page_id']}", "?context=edit&_fields=id,content")
        except Exception as e:
            print(f"  ✗ could not fetch page: {e} — skipping")
            continue

        raw = page.get("content", {}).get("raw", "")
        print(f"  Page raw: {len(raw)} chars")

        # Check if hero already present
        if 'class="article-hero"' in raw:
            print("  ✓ article-hero already present — skipping")
            continue

        # Build hero HTML
        hero_html = HERO_TEMPLATE.format(src=src, alt=alt)

        # Inject
        new_raw, ok = inject_hero(raw, hero_html)
        if not ok:
            print(f"  ✗ injection failed — skipping")
            continue

        print(f"  ✓ hero section built: {hero_html[:80]}...")

        if args.dry_run:
            # Show injection preview
            idx = new_raw.find('class="article-hero"')
            print(f"  [DRY] Preview:\n    {new_raw[max(0,idx-20):idx+120]}")
            continue

        # Push
        if wp_patch(env, f"/pages/{t['page_id']}", {"content": new_raw}):
            print(f"  ✓ pushed — hero injected into {t['label']}")
        else:
            print(f"  ✗ push failed for {t['label']}")

    print(f"\n{'='*50}")
    print("Done.")

if __name__ == "__main__":
    main()
