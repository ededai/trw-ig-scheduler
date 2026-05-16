#!/usr/bin/env python3
"""sync_topic_pages.py — backfill missing article cards on /topics/<pillar>/ pages.

Reads:
  - topic_tags.json: article slug -> list of pillar slugs
  - hub_classifier.json: article slug -> category (Guides/Car Tips/News)

For each pillar, fetches its WP page (child of /topics/, page 1597), identifies
the post-grid container, extracts existing card slugs, builds + injects cards for
any expected article not already present. ADD-only. Idempotent.

Usage:
  python3 sync_topic_pages.py --dry-run
  python3 sync_topic_pages.py
"""
from __future__ import annotations
import argparse, base64, json, os, re, sys
from pathlib import Path
from urllib import request, error

WP_ORIGIN = "https://therightworkshop.com"
TOPICS_PARENT_ID = 1597
HERE = Path(__file__).parent
TOPIC_TAGS_PATH = HERE / "topic_tags.json"
HUB_CLASSIFIER_PATH = HERE / "hub_classifier.json"

def load_env() -> dict:
    env = {}
    for key in ("WORDPRESS_USERNAME", "WORDPRESS_PASSWORD", "WORDPRESS_API_URL"):
        if os.environ.get(key):
            env[key] = os.environ[key]
    if len(env) == 3:
        return env
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
    return f"Basic {base64.b64encode(creds.encode()).decode()}"

def wp_get(env, path, params=""):
    url = f"{WP_ORIGIN}/wp-json/wp/v2{path}{params}"
    req = request.Request(url, headers={"Authorization": auth_header(env)})
    try:
        with request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except error.HTTPError as e:
        print(f"  GET {path} -> HTTP {e.code}")
        return None

def wp_push(env, page_id, content):
    url = f"{WP_ORIGIN}/wp-json/wp/v2/pages/{page_id}"
    body = json.dumps({
        "content": content,
        "meta": {"_trw_canonical_chrome": "yes"},
    }).encode()
    headers = {"Authorization": auth_header(env), "Content-Type": "application/json"}
    req = request.Request(url, data=body, method="POST", headers=headers)
    try:
        with request.urlopen(req, timeout=60) as r:
            r.read()
            return True
    except error.HTTPError as e:
        print(f"  PUSH {page_id} -> HTTP {e.code}: {e.read().decode()[:200]}")
        return False

def strip_html(s):
    return re.sub(r'<[^>]+>', '', s or '').strip()

def html_unescape(s):
    return (s or '').replace('&#8217;', "'").replace('&#8230;', '...').replace('&#038;', '&').replace('&amp;', '&').replace('&#8211;', '-')

def fetch_article_card_data(env, slug):
    """Return (title, hero_src, hero_alt, excerpt) or None if not found."""
    pages = wp_get(env, "/pages", f"?slug={slug}&context=edit&_fields=id,title,excerpt,content")
    if not pages:
        return None
    p = pages[0]
    title = html_unescape(strip_html(p.get("title", {}).get("rendered", slug)))
    excerpt = html_unescape(strip_html(p.get("excerpt", {}).get("rendered", "")))[:140]
    content = p.get("content", {}).get("raw", "")
    # Find hero from article-hero or first <img>
    m = re.search(r'<section class="article-hero">[\s\S]*?<img[^>]*src="([^"]+)"[^>]*alt="([^"]*)"', content)
    if m:
        src, alt = m.group(1), m.group(2)
    else:
        # Fallback: first img
        m2 = re.search(r'<img[^>]*src="([^"]+)"[^>]*alt="([^"]*)"', content)
        if not m2:
            return None
        src, alt = m2.group(1), m2.group(2)
    src = re.sub(r'^https?://i\d+\.wp\.com/', 'https://', src).split('?')[0]
    if not alt:
        alt = title
    return (title, src, alt, excerpt)

def build_card_html(slug, cat, title, hero_src, hero_alt, excerpt):
    return (
        f'<a class="post-card" data-cat="{cat}" href="/{slug}/">'
        f'<div class="pc-media"><img src="{hero_src}" alt="{hero_alt}" decoding="async"></div>'
        f'<div class="pc-body"><div class="pc-eyebrow">{cat}</div>'
        f'<h3>{title}</h3>'
        f'<p>{excerpt}</p>'
        f'<div class="pc-meta">By The Right Workshop team</div></div></a>'
    )

def extract_existing_slugs(raw):
    """Find all post-card hrefs in the raw page content."""
    return set(re.findall(r'class="post-card"[^>]*href="/([^"/]+)/"', raw))

def inject_cards(raw, new_cards_html):
    """Insert cards into the post-grid. Handle two patterns:
       A) <div class="post-grid"... id="postGrid"...> ... <div class="empty-state">...</div> ... </div>
          (new pages) — replace empty-state with cards
       B) <div class="post-grid">...</div> (legacy) — append before closing </div>
       C) ANY grid container with class containing 'grid' that holds existing post-cards
    """
    if not new_cards_html:
        return raw, False

    # Pattern A: empty-state placeholder
    es_re = re.compile(r'(<div class="post-grid"[^>]*>\s*)<div class="empty-state">[\s\S]*?</div>(\s*</div>)', re.IGNORECASE)
    m = es_re.search(raw)
    if m:
        return es_re.sub(m.group(1) + new_cards_html + m.group(2), raw), True

    # Pattern B: find post-grid container with existing cards inside
    # Append before closing tag of grid container
    grid_re = re.compile(r'(<div[^>]*class="[^"]*post-grid[^"]*"[^>]*>)([\s\S]*?)(</div>\s*(?:</section>|</div>|<!-- |<script))', re.IGNORECASE)
    m = grid_re.search(raw)
    if m:
        head, body, tail = m.group(1), m.group(2), m.group(3)
        return raw.replace(m.group(0), head + body + new_cards_html + tail), True

    # Pattern C: any div with 'grid' class containing post-card
    any_grid_re = re.compile(r'(<div[^>]*class="[^"]*grid[^"]*"[^>]*>)([\s\S]*?<a class="post-card"[\s\S]*?)(</div>\s*(?:</section>|</div>|<!--))', re.IGNORECASE)
    m = any_grid_re.search(raw)
    if m:
        head, body, tail = m.group(1), m.group(2), m.group(3)
        return raw.replace(m.group(0), head + body + new_cards_html + tail), True

    return raw, False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pillars", default="", help="Comma-separated pillar slugs to limit run")
    args = ap.parse_args()
    dry = args.dry_run
    pillars_filter = set(x.strip() for x in args.pillars.split(",") if x.strip())

    env = load_env()
    if not env.get("WORDPRESS_USERNAME"):
        sys.exit("ERROR: WP credentials missing")

    topic_tags = json.loads(TOPIC_TAGS_PATH.read_text())
    hub_classifier = json.loads(HUB_CLASSIFIER_PATH.read_text())

    # Build pillar -> list of article slugs
    pillar_to_articles = {}
    for slug, pillars in topic_tags.items():
        if slug.startswith("_") or not isinstance(pillars, list):
            continue
        for p in pillars:
            pillar_to_articles.setdefault(p, []).append(slug)

    print(f"Pillars in topic_tags: {len(pillar_to_articles)}")

    # Cache for article card data
    article_cache = {}
    total_added, total_skipped = 0, 0

    for pillar in sorted(pillar_to_articles.keys()):
        if pillars_filter and pillar not in pillars_filter:
            continue
        expected = pillar_to_articles[pillar]

        # Resolve pillar page id
        pages = wp_get(env, "/pages", f"?slug={pillar}&parent={TOPICS_PARENT_ID}&context=edit&_fields=id,slug,content")
        if not pages:
            print(f"  ✗ /topics/{pillar}/ — page not found")
            continue
        page = pages[0]
        pid, raw = page["id"], page.get("content", {}).get("raw", "")

        existing = extract_existing_slugs(raw)
        missing = [s for s in expected if s not in existing]

        if not missing:
            print(f"  ✓ /topics/{pillar}/ ({pid}) — already has {len(existing)} card(s), no adds needed")
            total_skipped += 1
            continue

        print(f"  + /topics/{pillar}/ ({pid}) — need to add {len(missing)} card(s): {missing}")

        # Build cards
        cards_html = ""
        for art_slug in missing:
            if art_slug not in article_cache:
                d = fetch_article_card_data(env, art_slug)
                if not d:
                    print(f"      ! could not fetch {art_slug}, skipping")
                    continue
                article_cache[art_slug] = d
            title, hero, alt, excerpt = article_cache[art_slug]
            cat = hub_classifier.get(art_slug, "Guides")
            cards_html += build_card_html(art_slug, cat, title, hero, alt, excerpt)

        if not cards_html:
            continue

        new_raw, ok = inject_cards(raw, cards_html)
        if not ok:
            print(f"      ✗ could not find post-grid in /topics/{pillar}/ — skipped")
            continue

        if dry:
            print(f"      [DRY] would push {len(missing)} cards to /topics/{pillar}/ (raw {len(raw)} -> {len(new_raw)})")
        else:
            if wp_push(env, pid, new_raw):
                print(f"      ✓ pushed {len(missing)} cards to /topics/{pillar}/")
                total_added += len(missing)
            else:
                print(f"      ✗ push failed")

    print(f"\nTotal pillars touched: {total_added // max(1, len(pillar_to_articles))}")
    print(f"Total cards added: {total_added} ({'DRY-RUN' if dry else 'LIVE'})")

if __name__ == "__main__":
    main()
