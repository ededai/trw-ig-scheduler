#!/usr/bin/env python3
"""Sync /blog/ (WP page 475) post cards — auto-adds new blog posts.

Runs daily in GitHub Actions. Idempotent — no-op when nothing has changed.

What it does:
  1. Fetches all published WP pages assigned to Guides / Car Tips / News.
  2. Parses the current /blog/ HTML from WP page 475.
  3. Adds any missing post cards (hero + category read from article content).
  4. Pushes back to WP only when changes were made.

Category is read from <div class="article-eyebrow"> inside the article,
NOT from WP taxonomy — the WP REST API does not expose page categories
in the response body, so using taxonomy would silently default everything
to Guides and corrupt Car Tips / News cards.

To change a card's category: edit push_blog_hub.py POSTS_MANIFEST and
re-run it, or run fix_post_categories.py to fix WP taxonomy first.

Category IDs (therightworkshop.com):
  Guides = 1367 | Car Tips = 1368 | News = 1369

Usage:
  python3 sync_blog_hub_posts.py           # live run
  python3 sync_blog_hub_posts.py --dry-run # preview, no writes
"""
from __future__ import annotations
import argparse, base64, json, os, re, sys
from pathlib import Path
from urllib import request, error
try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("bs4 required: pip install beautifulsoup4 lxml")

BLOG_PAGE_ID = 475
CAT_IDS      = [1367, 1368, 1369]          # Guides, Car Tips, News
CAT_NAMES    = {1367: "Guides", 1368: "Car Tips", 1369: "News"}
WP_ORIGIN    = "https://therightworkshop.com"

# Classifier: slug -> category. Single source of truth for hub assignment.
# Cole/Bryan/Codi append entries at publish time.
CLASSIFIER_PATH = Path(__file__).parent / "hub_classifier.json"
HUB_CLASSIFIER: dict[str, str] = {}
if CLASSIFIER_PATH.exists():
    try:
        _raw = json.loads(CLASSIFIER_PATH.read_text())
        HUB_CLASSIFIER = {k: v for k, v in _raw.items() if not k.startswith("_")}
    except Exception as e:
        print(f"WARN: failed to load {CLASSIFIER_PATH.name}: {e}")

# ── credentials ──────────────────────────────────────────────────────────────

def load_env() -> dict:
    """Accept credentials from env vars (GH Actions) or local .env file."""
    env: dict = {}
    # Env vars take precedence (GitHub Actions)
    for key in ("WORDPRESS_USERNAME", "WORDPRESS_PASSWORD", "WORDPRESS_API_URL"):
        if os.environ.get(key):
            env[key] = os.environ[key]
    if len(env) == 3:
        return env
    # Fallback: local .env file
    for candidate in [
        Path("/Users/admin/the-right-workshop/tools/.env"),
        Path(__file__).parent.parent / "tools" / ".env",
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


def auth_header(env: dict) -> str:
    creds = f"{env['WORDPRESS_USERNAME']}:{env['WORDPRESS_PASSWORD']}"
    return f"Basic {base64.b64encode(creds.encode()).decode()}"


# ── WP helpers ────────────────────────────────────────────────────────────────

def wp_get(env: dict, path: str, params: str = "") -> list | dict | None:
    url = f"{WP_ORIGIN}/wp-json/wp/v2{path}{params}"
    req = request.Request(url, headers={"Authorization": auth_header(env)})
    try:
        with request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except error.HTTPError as e:
        print(f"  GET {path} → HTTP {e.code}")
        return None


def wp_push(env: dict, page_id: int, content: str) -> bool:
    url = f"{WP_ORIGIN}/wp-json/wp/v2/pages/{page_id}"
    body = json.dumps({
        "content": content,
        "template": "elementor_canvas",
        "meta": {"_trw_canonical_chrome": ""},  # page has its own nav/footer; disable WP injection
    }).encode()
    headers = {"Authorization": auth_header(env), "Content-Type": "application/json"}
    req = request.Request(url, data=body, method="POST", headers=headers)
    try:
        with request.urlopen(req, timeout=60) as r:
            r.read()
            return True
    except error.HTTPError as e:
        print(f"  PUSH page {page_id} → HTTP {e.code}: {e.read().decode()[:200]}")
        return False


def fetch_blog_page_raw(env: dict) -> str:
    """Fetch raw HTML content of /blog/ (page 475) from WP."""
    data = wp_get(env, f"/pages/{BLOG_PAGE_ID}", "?context=edit&_fields=content")
    if not data:
        sys.exit("ERROR: could not fetch /blog/ page from WP.")
    raw = data.get("content", {}).get("raw", "")
    if not raw:
        sys.exit("ERROR: /blog/ content is empty.")
    return raw


def fetch_all_blog_pages(env: dict) -> list[dict]:
    """Fetch all published WP pages assigned to Guides/Car Tips/News."""
    cat_str = ",".join(map(str, CAT_IDS))
    pages = wp_get(
        env, "/pages",
        f"?categories={cat_str}&per_page=100&orderby=date&order=desc"
        f"&status=publish&_fields=id,slug,title,excerpt,categories"
    )
    return pages or []


def fetch_hero_and_cat(env: dict, page_id: int) -> tuple[str, str, str]:
    """Extract hero img src, alt, and category label.

    Hero lookup order (changed 2026-05-16, see Cole task NEWS_TEMPLATE_V3_HANDOFF):
      1. WP featured_media (canonical — works for news articles which deliberately
         do NOT emit an in-body article-hero img).
      2. <section class="article-hero"><img>  (legacy blog-chrome posts).
    Category: read from <div class="article-eyebrow"> inside content.
    """
    data = wp_get(env, f"/pages/{page_id}", "?context=edit&_fields=content,featured_media")
    if not data:
        return ("", "", "")
    content = data.get("content", {}).get("raw", "")

    # 1. featured_media first
    fm_id = data.get("featured_media") or 0
    src, alt = "", ""
    if fm_id:
        media = wp_get(env, f"/media/{fm_id}", "?_fields=source_url,alt_text")
        if media and media.get("source_url"):
            src = re.sub(r'^https?://i\d+\.wp\.com/', 'https://', media["source_url"]).split('?')[0]
            alt = media.get("alt_text") or ""

    # 2. fallback: article-hero img in body
    if not src:
        m = re.search(
            r'<section class="article-hero">.*?<img[^>]*src="([^"]+)"[^>]*alt="([^"]*)"',
            content, re.S
        )
        if m:
            src = re.sub(r'^https?://i\d+\.wp\.com/', 'https://', m.group(1)).split('?')[0]
            alt = m.group(2)

    if not src:
        return ("", "", "")

    # Extract category from eyebrow inside article body
    cat_m = re.search(r'<div class="article-eyebrow[^"]*"[^>]*>([^<]+)</div>', content)
    cat = cat_m.group(1).strip() if cat_m else ""
    if cat not in CAT_NAMES.values():
        cat = "Guides"
    return (src, alt, cat)


def strip_html(s: str) -> str:
    return re.sub(r'<[^>]+>', '', s or '').strip()


# ── image-refresh pass ────────────────────────────────────────────────────────

def refresh_existing_card_images(env: dict, raw: str, dry: bool = False) -> tuple[str, int]:
    """Refresh featured_media img src on every existing post-card in raw HTML.

    For each <a class="post-card"> block found in raw:
      1. Extracts the href slug.
      2. Queries WP REST /posts?slug=… then /pages?slug=… (posts first) for
         featured_media.
      3. If featured_media > 0, fetches /media/{id} for source_url + alt_text.
      4. Strips Jetpack proxy prefix and query-string args.
      5. Replaces img src/alt in that card's HTML when the src has changed.

    Returns (updated_raw, changes_count).
    """
    # Find every post-card block: from the opening <a class="post-card" to </a>
    card_re = re.compile(
        r'(<a\s[^>]*class="[^"]*post-card[^"]*"[^>]*href="/([^"]+)/"[^>]*>.*?</a>)',
        re.S,
    )
    changes = 0
    updated = raw

    for m in card_re.finditer(raw):
        card_html = m.group(1)
        slug = m.group(2).strip("/")
        if not slug:
            continue

        # Current img src in card
        img_m = re.search(r'<img[^>]*src="([^"]+)"[^>]*>', card_html)
        if not img_m:
            continue
        current_src = img_m.group(1)

        # Resolve featured_media — try posts, then pages
        fm_id = 0
        for endpoint in ("/posts", "/pages"):
            data = wp_get(env, endpoint,
                          f"?slug={slug}&status=publish&_fields=id,featured_media")
            if data:
                row = data[0] if isinstance(data, list) else data
                fm_id = (row or {}).get("featured_media") or 0
                if fm_id:
                    break

        if not fm_id:
            continue

        media = wp_get(env, f"/media/{fm_id}", "?_fields=source_url,alt_text")
        if not media or not media.get("source_url"):
            continue

        new_src = re.sub(r'^https?://i\d+\.wp\.com/', 'https://',
                         media["source_url"]).split('?')[0]
        new_alt = media.get("alt_text") or ""

        if new_src == current_src:
            continue  # already current

        print(f"  REFRESH /{slug}/ → {new_src.split('/')[-1]}")
        if not dry:
            # Replace src (and alt if present) inside this card's HTML
            new_card = re.sub(
                r'(<img[^>]*\ssrc=")[^"]+(")',
                lambda _m: _m.group(1) + new_src + _m.group(2),
                card_html,
            )
            new_card = re.sub(
                r'(<img[^>]*\salt=")[^"]*(")',
                lambda _m: _m.group(1) + new_alt + _m.group(2),
                new_card,
            )
            # Replace the exact card block in updated (use first occurrence)
            updated = updated.replace(card_html, new_card, 1)
        changes += 1

    return updated, changes


def build_card(slug: str, cat: str, title: str, excerpt: str,
               hero_src: str, hero_alt: str) -> str:
    return (
        f'<a class="post-card" data-cat="{cat}" href="/{slug}/">'
        f'<div class="pc-media"><img src="{hero_src}" alt="{hero_alt}" data-recalc-dims="1" decoding="async"></div>'
        f'<div class="pc-body"><div class="pc-eyebrow">{cat}</div>'
        f'<h3>{title}</h3>'
        f'<p>{excerpt[:140]}</p>'
        f'<div class="pc-meta">By The Right Workshop team</div></div></a>'
    )


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    dry = args.dry_run
    label = " [DRY RUN]" if dry else ""
    print(f"sync_blog_hub_posts{label}")

    env = load_env()
    if not env.get("WORDPRESS_USERNAME"):
        sys.exit("ERROR: WP credentials not found.")

    # 1. Fetch all blog posts from WP taxonomy
    print("Fetching WP pages with blog categories...")
    wp_pages = fetch_all_blog_pages(env)
    print(f"  Found {len(wp_pages)} pages in Guides/Car Tips/News")

    # 2. Fetch current /blog/ HTML
    print("Fetching current /blog/ HTML...")
    raw_html = fetch_blog_page_raw(env)

    # 3. Parse with bs4 — preserve the wp:html wrapper
    if raw_html.strip().startswith("<!-- wp:html -->"):
        inner = re.sub(r'^<!-- wp:html -->\s*', '', raw_html)
        inner = re.sub(r'\s*<!-- /wp:html -->$', '', inner)
        wrap = True
    else:
        inner = raw_html
        wrap = False

    soup = BeautifulSoup(inner, "html.parser")
    grid = soup.find(id="postGrid")
    if not grid:
        sys.exit("ERROR: #postGrid not found in /blog/ HTML.")

    # Build index: href → card element, for existing cards
    existing: dict[str, object] = {}
    for card in grid.find_all("a", class_="post-card"):
        href = card.get("href", "").strip("/")
        if href:
            existing[href] = card

    changes = 0

    # UPDATE PASS: fix existing cards whose img src is still the oil-pour default.
    # Iterates existing grid cards directly — catches articles not in WP taxonomy categories
    # (e.g. news posts mis-catted or un-catted), which wp_pages would silently skip.
    # Only updates the img element — never touches category, title, excerpt, or href.
    OIL_POUR_DEFAULT = 958  # WP media ID for nb_servicing_oilpour_v2.webp
    for slug, card in list(existing.items()):
        img = card.find("img")
        if not img:
            continue
        current_src = img.get("src", "")
        if "nb_servicing_oilpour" not in current_src:
            continue  # already has a real image

        # Look up the WP page by slug to get featured_media
        pages_data = wp_get(env, "/pages",
                            f"?slug={slug}&status=publish&_fields=id,featured_media")
        if not pages_data:
            print(f"  UPDATE /{slug}/ — WP page not found, skipping")
            continue
        page_data = pages_data[0] if isinstance(pages_data, list) else pages_data
        fm_id = (page_data or {}).get("featured_media") or 0
        if not fm_id or fm_id == OIL_POUR_DEFAULT:
            continue  # featured_media not set or still points at default

        media = wp_get(env, f"/media/{fm_id}", "?_fields=source_url,alt_text")
        if not media or not media.get("source_url"):
            continue

        new_src = re.sub(r'^https?://i\d+\.wp\.com/', 'https://', media["source_url"]).split('?')[0]
        new_alt = media.get("alt_text") or ""
        if new_src == current_src:
            continue

        print(f"  UPDATE /{slug}/ — refreshing image → {new_src.split('/')[-1]}")
        if not dry:
            img["src"] = new_src
            img["alt"] = new_alt
        changes += 1

    for page in wp_pages:
        slug = page.get("slug", "")
        if not slug:
            continue

        # Skip slugs already in the grid (category managed by push_blog_hub.py).
        # UPDATE pass above handles image-only refreshes for existing cards.
        if slug in existing:
            continue

        print(f"  ADD   /{slug}/ — fetching hero and category...")
        hero_src, hero_alt, cat = fetch_hero_and_cat(env, page["id"])
        if not hero_src:
            print(f"        WARN: no hero found for /{slug}/ — skipping")
            continue
        title   = strip_html(page.get("title", {}).get("rendered", slug))
        excerpt = strip_html(page.get("excerpt", {}).get("rendered", ""))
        card_html = build_card(slug, cat, title, excerpt, hero_src, hero_alt)
        if not dry:
            grid.append(BeautifulSoup(card_html, "html.parser").find("a"))
        print(f"        cat={cat} hero={hero_src[:60]}")
        changes += 1

    print(f"{changes} structural change(s) {'would be' if dry else 'made'}.")

    if dry:
        return

    # 4. Serialise soup changes
    updated_inner = str(soup)  # html.parser doesn't add <html><body> wrappers
    if wrap:
        interim_raw = f"<!-- wp:html -->\n{updated_inner.strip()}\n<!-- /wp:html -->"
    else:
        interim_raw = updated_inner

    # 5. Full image-refresh pass — updates ALL card img srcs from WP featured_media.
    #    Runs every sync so stale images are fixed even when no cards were added.
    print("Running full image-refresh pass on existing cards...")
    new_raw, img_changes = refresh_existing_card_images(env, interim_raw, dry=False)
    if img_changes:
        print(f"  Refreshed {img_changes} card image(s).")
        changes += img_changes
    else:
        print("  All card images already current.")
        new_raw = interim_raw  # no modification

    if changes == 0:
        print("No changes needed — /blog/ is up to date.")
        return

    print("Pushing to WP...")
    if wp_push(env, BLOG_PAGE_ID, new_raw):
        print(f"OK — /blog/ updated with {changes} change(s).")
    else:
        sys.exit("PUSH FAILED")


if __name__ == "__main__":
    main()
