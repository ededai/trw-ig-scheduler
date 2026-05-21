#!/usr/bin/env python3
"""fix_topic_page.py — repair any /topics/<pillar>/ page.

Fixes two bugs in one pass:
  1. Embedded chrome (nav + mobile-nav + footer + hamburger JS) left over from
     before Snippet 25 (canonical chrome) was applied. Strips them so only the
     canonical chrome renders.
  2. Broken post-grid caused by old inject_cards regex nesting cards inside
     the first card's .pc-meta. Extracts all post-card slugs from the broken
     HTML, fetches fresh article data from WP for each, rebuilds the post-grid
     with all cards as flat siblings.

Also updates:
  - Hero count ("N posts")
  - window.TRW_SEARCH_CORPUS
  - JSON-LD numberOfItems

Usage:
  python3 fix_topic_page.py workshop
  python3 fix_topic_page.py servicing
  python3 fix_topic_page.py --all       # all pillars that have embedded chrome
  python3 fix_topic_page.py --dry-run workshop
"""
from __future__ import annotations
import argparse, base64, json, os, re, sys
from pathlib import Path
from urllib import request, error

WP_ORIGIN = "https://therightworkshop.com"
TOPICS_PARENT_ID = 1597
HERE = Path(__file__).parent

CHROME_PATTERNS = [
    # nav block: <!-- NAV --> ... </nav> + mobile-nav div
    (re.compile(
        r'\n?<!-- NAV -->\n<nav\b[\s\S]*?</nav>\n<div class="mobile-nav"[\s\S]*?</div>\n?'
    ), '\n'),
    # footer block
    (re.compile(
        r'\n?<!-- FOOTER -->\n<footer[\s\S]*?</footer>\n?'
    ), '\n'),
    # hamburger JS
    (re.compile(
        r'\n?<script>\s*\(function\(\)\{\s*const btn = document\.getElementById\(\'navHamburger\'[\s\S]*?\}\)\(\);\s*</script>\n?'
    ), '\n'),
]

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
        with request.urlopen(req, timeout=20) as r:
            return r.status in (200, 201)
    except error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.read().decode()[:300]}")
        return False

def strip_chrome(raw: str) -> tuple[str, bool]:
    changed = False
    for pattern, replacement in CHROME_PATTERNS:
        new = pattern.sub(replacement, raw, count=1)
        if new != raw:
            changed = True
            raw = new
    return raw, changed

def has_embedded_chrome(raw: str) -> bool:
    return '<footer' in raw or '<nav class="nav"' in raw

def extract_slugs(raw: str) -> list[str]:
    """Extract all post-card hrefs preserving order, deduplicating."""
    seen, slugs = set(), []
    for slug in re.findall(r'class="post-card"[^>]*href="/([^"/]+)/"', raw):
        if slug not in seen:
            seen.add(slug)
            slugs.append(slug)
    return slugs

def resolve_hero(env, article_id, featured_media_id):
    if featured_media_id:
        try:
            m = wp_get(env, f"/media/{featured_media_id}", "?_fields=source_url,alt_text")
            src = re.sub(r'^https?://i\d+\.wp\.com/', 'https://', m.get("source_url","")).split("?")[0]
            return src, m.get("alt_text","") or ""
        except Exception:
            pass
    return "", ""

def fetch_card_data(env, slug):
    try:
        posts = wp_get(env, "/posts", f"?slug={slug}&_fields=id,title,excerpt,featured_media,categories")
        if not posts:
            posts = wp_get(env, "/pages", f"?slug={slug}&_fields=id,title,excerpt,featured_media")
        if not posts:
            return None
        p = posts[0]
        title = p.get("title",{}).get("rendered","").strip()
        excerpt = re.sub(r'<[^>]+>', '', p.get("excerpt",{}).get("rendered","")).strip()
        excerpt = excerpt[:160]
        hero_src, hero_alt = resolve_hero(env, p["id"], p.get("featured_media") or 0)
        if not hero_src:
            # fallback: first img in content
            content = p.get("content",{}).get("rendered","")
            m2 = re.search(r'<img[^>]*src="([^"]+)"[^>]*alt="([^"]*)"', content)
            if m2:
                hero_src = re.sub(r'^https?://i\d+\.wp\.com/', 'https://', m2.group(1)).split("?")[0]
                hero_alt = m2.group(2)
        return title, hero_src, hero_alt or title, excerpt
    except Exception as e:
        print(f"    ! fetch_card_data({slug}): {e}")
        return None

def build_card(slug, cat, title, img_url, img_alt, excerpt):
    return (
        f'<a class="post-card" data-cat="{cat}" href="/{slug}/">'
        f'<div class="pc-media"><img data-recalc-dims="1" loading="lazy" '
        f'src="{img_url}" alt="{img_alt}" decoding="async"></div>'
        f'<div class="pc-body"><div class="pc-eyebrow">{cat}</div>'
        f'<h3>{title}</h3><p>{excerpt}</p>'
        f'<div class="pc-meta">By The Right Workshop team</div></div></a>'
    )

def _find_div_close(raw, start):
    depth, i = 0, start
    open_re = re.compile(r'<div\b', re.IGNORECASE)
    close_re = re.compile(r'</div\s*>', re.IGNORECASE)
    while i < len(raw):
        om = open_re.search(raw, i)
        cm = close_re.search(raw, i)
        if not cm:
            break
        if om and om.start() < cm.start():
            depth += 1
            i = om.end()
        else:
            if depth == 0:
                return cm.start()
            depth -= 1
            i = cm.end()
    return -1

def rebuild_grid(raw, cards_html):
    grid_open_re = re.compile(r'<div[^>]*class="[^"]*post-grid[^"]*"[^>]*>', re.IGNORECASE)
    m = grid_open_re.search(raw)
    if not m:
        return raw, False
    grid_inner_start = m.end()
    grid_close = _find_div_close(raw, grid_inner_start)
    if grid_close < 0:
        return raw, False
    new_raw = raw[:grid_inner_start] + cards_html + raw[grid_close:]
    return new_raw, True

def build_search_corpus(cards):
    entries = []
    for slug, _, title, *_ in cards:
        plain = re.sub(r'&#\d+;', lambda m: chr(int(m.group()[2:-1])), title)
        plain = plain.replace("&amp;","&").replace("&quot;",'"')
        entries.append({"n": plain, "u": f"/{slug}/"})
    return json.dumps(entries, ensure_ascii=False)

def fix_pillar(env, pillar, dry=False, hub_classifier=None):
    print(f"\n{'='*50}")
    print(f"Fixing /topics/{pillar}/")

    pages = wp_get(env, "/pages",
        f"?slug={pillar}&parent={TOPICS_PARENT_ID}&context=edit&_fields=id,slug,content")
    if not pages:
        print(f"  ✗ page not found")
        return False
    page = pages[0]
    pid, raw = page["id"], page.get("content",{}).get("raw","")
    print(f"  Page ID: {pid} | Raw: {len(raw)} chars")

    if not has_embedded_chrome(raw) and '<a class="post-card"' not in raw:
        print(f"  ✓ no embedded chrome, no cards — skipping")
        return True

    # 1. Strip embedded chrome
    raw, chrome_stripped = strip_chrome(raw)
    if chrome_stripped:
        print(f"  ✓ stripped embedded chrome")
    else:
        print(f"  - no embedded chrome found")

    # 2. Extract all slugs from broken grid
    slugs = extract_slugs(raw)
    print(f"  Found {len(slugs)} card slugs: {slugs[:5]}{'...' if len(slugs)>5 else ''}")

    if not slugs:
        if dry:
            print(f"  [DRY] would push chrome-stripped content only")
        else:
            if wp_patch(env, f"/pages/{pid}", {"content": raw}):
                print(f"  ✓ pushed chrome-stripped content (no cards to rebuild)")
        return True

    # 3. Fetch article data for each slug
    card_tuples = []
    for slug in slugs:
        data = fetch_card_data(env, slug)
        if not data:
            print(f"    ! skipping {slug} — could not fetch")
            continue
        title, hero_src, hero_alt, excerpt = data
        cat = (hub_classifier or {}).get(slug, "Guides")
        card_tuples.append((slug, cat, title, hero_src, hero_alt, excerpt))
        print(f"    + {slug[:50]} [{cat}] img={'OK' if hero_src else 'MISSING'}")

    # 4. Rebuild grid
    cards_html = "".join(build_card(*t) for t in card_tuples)
    raw, ok = rebuild_grid(raw, cards_html)
    if not ok:
        print(f"  ✗ could not find post-grid — aborting")
        return False
    print(f"  ✓ rebuilt post-grid with {len(card_tuples)} flat cards")

    # 5. Update count
    n = len(card_tuples)
    label = f"{n} post{'s' if n != 1 else ''}"
    raw = re.sub(r'<div class="count">\d+[^<]*</div>', f'<div class="count">{label}</div>', raw)

    # 6. Update search corpus
    corpus = build_search_corpus(card_tuples)
    raw = re.sub(r'window\.TRW_SEARCH_CORPUS=\[.*?\];', f'window.TRW_SEARCH_CORPUS={corpus};', raw)

    # 7. Update JSON-LD
    raw = re.sub(r'"numberOfItems":\s*\d+', f'"numberOfItems": {n}', raw)

    if dry:
        idx = raw.find('class="post-grid"')
        print(f"\n[DRY] Post-grid preview:\n{raw[idx:idx+300]}")
        print(f"[DRY] Count: {label}")
        return True

    if wp_patch(env, f"/pages/{pid}", {"content": raw}):
        print(f"  ✓ pushed — {label}, chrome clean")
        return True
    else:
        print(f"  ✗ push failed")
        return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pillars", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    env = load_env()
    if not env.get("WORDPRESS_USERNAME"):
        sys.exit("ERROR: WP credentials missing")

    hub_classifier = {}
    hc_path = HERE / "hub_classifier.json"
    if hc_path.exists():
        hub_classifier = json.loads(hc_path.read_text())

    if args.all:
        # fetch all topic page children and check each
        all_pages = wp_get(env, "/pages",
            f"?parent={TOPICS_PARENT_ID}&per_page=100&context=edit&_fields=id,slug,content")
        pillars = []
        for p in all_pages:
            raw = p.get("content",{}).get("raw","")
            if has_embedded_chrome(raw):
                pillars.append(p["slug"])
        print(f"Pages with embedded chrome: {pillars}")
    else:
        pillars = args.pillars

    if not pillars:
        print("Usage: fix_topic_page.py <pillar> [<pillar>...] | --all")
        sys.exit(1)

    results = {}
    for pillar in pillars:
        results[pillar] = fix_pillar(env, pillar, dry=args.dry_run,
                                     hub_classifier=hub_classifier)

    print(f"\n{'='*50}")
    print("RESULTS:")
    for p, ok in results.items():
        print(f"  {'✓' if ok else '✗'} /topics/{p}/")

if __name__ == "__main__":
    main()
