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
    """Extract hero img src, alt, and category label from the article's WP content."""
    data = wp_get(env, f"/pages/{page_id}", "?context=edit&_fields=content")
    if not data:
        return ("", "", "")
    content = data.get("content", {}).get("raw", "")
    m = re.search(
        r'<section class="article-hero">.*?<img[^>]*src="([^"]+)"[^>]*alt="([^"]*)"',
        content, re.S
    )
    if not m:
        return ("", "", "")
    src = m.group(1)
    src = re.sub(r'^https?://i\d+\.wp\.com/', 'https://', src).split('?')[0]
    # Extract category from eyebrow inside article-hero
    cat_m = re.search(r'<div class="article-eyebrow[^"]*"[^>]*>([^<]+)</div>', content)
    cat = cat_m.group(1).strip() if cat_m else ""
    # Validate against known categories; fall back to Guides
    if cat not in CAT_NAMES.values():
        cat = "Guides"
    return (src, m.group(2), cat)


def strip_html(s: str) -> str:
    return re.sub(r'<[^>]+>', '', s or '').strip()


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

    for page in wp_pages:
        slug = page.get("slug", "")
        if not slug:
            continue

        # Only process slugs not already in the grid (ADD-only; never mutate existing cards).
        # Category management is handled by push_blog_hub.py + fix_post_categories.py.
        # WP REST API does not expose the category taxonomy on pages in the response body,
        # so reading it here would always default to Guides and corrupt Car Tips / News cards.
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

    if changes == 0:
        print("No changes needed — /blog/ is up to date.")
        return

    print(f"{changes} change(s) {'would be' if dry else 'made'}.")

    if dry:
        return

    # 4. Serialise + push
    updated_inner = str(soup)  # html.parser doesn't add <html><body> wrappers
    if wrap:
        new_raw = f"<!-- wp:html -->\n{updated_inner.strip()}\n<!-- /wp:html -->"
    else:
        new_raw = updated_inner

    print("Pushing to WP...")
    if wp_push(env, BLOG_PAGE_ID, new_raw):
        print(f"OK — /blog/ updated with {changes} change(s).")
    else:
        sys.exit("PUSH FAILED")


if __name__ == "__main__":
    main()
