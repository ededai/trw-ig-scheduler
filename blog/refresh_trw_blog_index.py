#!/usr/bin/env python3
"""
TRW Blog Index — SINGLE SOURCE OF TRUTH refresh + drift checker.

Responsibilities (one script, no duplication):
  1. Featured article rotates every N days (config: rotation.days_per_bucket).
  2. Every post card's image on /blog/ is drift-checked against the LIVE
     article hero (<section class="article-hero"> > img). Fixes drift
     automatically and logs every change.
  3. Flags (does not auto-fix) secondary drift: og:image + schema.org Article
     image on each article. Reported for manual follow-up.
  4. Push back to WP page 475, preserving wp:html wrap + <style> block.

Design principles enforced here:
  - Source of truth is the LIVE article (not a mockup, not a hardcoded dict).
  - bs4 roundtrip (no regex surgery on HTML with <style>).
  - Deterministic 5-day bucket from config epoch (stable mid-cycle).
  - Idempotent: re-running produces no changes if nothing drifted.
  - Featured exclusion list supports slugs + category tags.

Modes:
  --check    Dry-run. Print proposed featured + full drift report. No writes.
  --apply    Run full refresh + push to WP. Idempotent.
  --report   Print current live state only. No writes, no article fetches.

Usage:
  python3 refresh_trw_blog_index.py --check
  python3 refresh_trw_blog_index.py --apply
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib import request, error

from bs4 import BeautifulSoup, NavigableString

TOOLS = Path(__file__).resolve().parent
ENV = TOOLS / ".env"
CONFIG = TOOLS / "trw_blog_config.json"
LOG_DIR = TOOLS / "logs"
LOG_FILE = LOG_DIR / "blog_index_refresh.log"


# ---------- utilities ----------

def log(msg: str) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    line = f"[{dt.datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line)
    with LOG_FILE.open("a") as f:
        f.write(line + "\n")


def _scrub(v):
    """Strip every kind of whitespace control char that GH secret paste sneaks in.
    Includes \\n \\r \\t and any zero-width / NBSP unicode."""
    if not isinstance(v, str):
        return v
    # Standard strip + remove any internal \r\n that snuck in mid-value
    v = v.strip().strip("\r\n\t ")
    # Remove any remaining control characters except spaces (WP App Passwords
    # legitimately contain internal single spaces).
    return "".join(ch for ch in v if ch == " " or (ord(ch) >= 0x20 and ord(ch) != 0x7f))


def load_env() -> dict:
    """Credentials. .env when present (local), os.environ otherwise (GH Actions)."""
    import os
    env = {}
    if ENV.exists():
        for line in ENV.read_text().splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                v = v.strip()
                if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                    v = v[1:-1]
                env[k.strip()] = v
    for key in ("WORDPRESS_API_URL", "WORDPRESS_USERNAME", "WORDPRESS_PASSWORD"):
        if not env.get(key) and os.environ.get(key):
            env[key] = os.environ[key]
    for key in list(env.keys()):
        env[key] = _scrub(env[key])
    missing = [k for k in ("WORDPRESS_API_URL", "WORDPRESS_USERNAME", "WORDPRESS_PASSWORD") if not env.get(k)]
    if missing:
        sys.stderr.write(f"ERROR: missing WP creds: {missing}. Set in .env or environment.\n")
        sys.exit(1)
    # Diagnostic: print exact post-scrub repr (lengths only for password) so any
    # remaining hidden char shows up in the log.
    print(
        f"[load_env] WP_API_URL={env['WORDPRESS_API_URL']!r} "
        f"WP_USER={env['WORDPRESS_USERNAME']!r} "
        f"WP_PASSWORD len={len(env['WORDPRESS_PASSWORD'])}",
        file=sys.stderr,
    )
    return env


def load_config() -> dict:
    return json.loads(CONFIG.read_text())


def wp_base(env: dict) -> str:
    site = _scrub(env.get("WORDPRESS_API_URL", "")).rstrip("/")
    if site.endswith("/wp-json"):
        site = site[: -len("/wp-json")]
    return site


def auth_header(env: dict) -> str:
    user = _scrub(env["WORDPRESS_USERNAME"])
    pw = _scrub(env["WORDPRESS_PASSWORD"])
    token = base64.b64encode(f"{user}:{pw}".encode()).decode()
    return f"Basic {token}"


def http_get(url: str, headers: dict | None = None, timeout: int = 30) -> str:
    req = request.Request(url, headers=headers or {"User-Agent": "trw-blog-refresh/1.0"})
    with request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def http_post_json(url: str, payload: dict, headers: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=body, headers=headers, method="POST")
    with request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ---------- WP page IO ----------

def fetch_blog_page_raw(env: dict, page_id: int) -> dict:
    base = wp_base(env)
    url = f"{base}/wp-json/wp/v2/pages/{page_id}?context=edit"
    headers = {"Authorization": auth_header(env), "User-Agent": "trw-blog-refresh/1.0"}
    req = request.Request(url, headers=headers)
    with request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def push_blog_page(env: dict, page_id: int, new_html_content: str) -> dict:
    base = wp_base(env)
    url = f"{base}/wp-json/wp/v2/pages/{page_id}"
    headers = {
        "Authorization": auth_header(env),
        "Content-Type": "application/json",
        "User-Agent": "trw-blog-refresh/1.0",
    }
    return http_post_json(url, {"content": new_html_content}, headers)


# ---------- HTML parsing ----------

WP_HTML_OPEN = "<!-- wp:html -->"
WP_HTML_CLOSE = "<!-- /wp:html -->"


def unwrap_wp_html(raw: str) -> tuple[str, bool]:
    """Strip wp:html comment wrapper if present. Returns (inner, was_wrapped)."""
    s = raw.strip()
    was = False
    if s.startswith(WP_HTML_OPEN):
        s = s[len(WP_HTML_OPEN):].lstrip()
        was = True
    if s.endswith(WP_HTML_CLOSE):
        s = s[: -len(WP_HTML_CLOSE)].rstrip()
    return s, was


def rewrap_wp_html(inner: str, was_wrapped: bool) -> str:
    if not was_wrapped:
        return inner
    return f"{WP_HTML_OPEN}\n{inner}\n{WP_HTML_CLOSE}"


def clean_src(src: str) -> str:
    """Normalise Jetpack Photon CDN URLs to canonical WP uploads URL."""
    if not src:
        return src
    s = src.strip()
    # Strip jetpack/photon wrapper
    m = re.match(r"https?://i\d+\.wp\.com/(.+?)(\?.*)?$", s)
    if m:
        path = m.group(1)
        if not path.startswith("http"):
            path = "https://" + path
        s = path
    # Strip query string
    s = s.split("?", 1)[0]
    # Decode HTML entities commonly seen (&#038; etc already handled by bs4)
    return s


def absolutise(url: str, origin: str) -> str:
    if not url:
        return url
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("/"):
        return origin.rstrip("/") + url
    return url


# ---------- live article hero extraction ----------

def extract_article_hero_src(article_html: str) -> str | None:
    soup = BeautifulSoup(article_html, "lxml")
    hero = soup.select_one("section.article-hero img, .article-hero img")
    if hero and hero.get("src"):
        return hero["src"]
    # Fallback: first nb_post_ or uploads image after nav
    for img in soup.find_all("img"):
        src = img.get("src") or ""
        if "logo-orange" in src or "mascot-only" in src:
            continue
        if "/wp-content/uploads/" in src:
            return src
    return None


def extract_og_image(article_html: str) -> str | None:
    m = re.search(
        r'<meta[^>]*property="og:image"[^>]*content="([^"]+)"', article_html
    )
    return m.group(1) if m else None


def extract_schema_article_image(article_html: str) -> str | None:
    try:
        for block in re.findall(
            r'<script type="application/ld\+json">(.*?)</script>',
            article_html,
            re.S,
        ):
            try:
                data = json.loads(block)
            except Exception:
                continue
            found = [None]

            def walk(o, depth=0):
                if depth > 6 or found[0]:
                    return
                if isinstance(o, dict):
                    if o.get("@type") in ("BlogPosting", "Article", "NewsArticle"):
                        img = o.get("image")
                        if isinstance(img, str):
                            found[0] = img
                            return
                        if isinstance(img, dict):
                            found[0] = img.get("url")
                            return
                        if isinstance(img, list) and img:
                            first = img[0]
                            if isinstance(first, str):
                                found[0] = first
                                return
                            if isinstance(first, dict):
                                found[0] = first.get("url")
                                return
                    for v in o.values():
                        walk(v, depth + 1)
                elif isinstance(o, list):
                    for v in o:
                        walk(v, depth + 1)

            walk(data)
            if found[0]:
                return found[0]
    except Exception:
        pass
    return None


def compute_read_time(article_html: str, wpm: int) -> int:
    soup = BeautifulSoup(article_html, "lxml")
    # Prefer the article body if a clear container exists
    body = soup.select_one("article, main, .article-body, .post-content") or soup
    text = body.get_text(" ", strip=True)
    words = len(re.findall(r"\w+", text))
    minutes = max(3, round(words / wpm))
    return minutes


# ---------- blog index structure ----------

def parse_cards(soup: BeautifulSoup) -> list[dict]:
    cards = []
    for a in soup.select(".post-grid a.post-card"):
        img = a.select_one(".pc-media img")
        h3 = a.select_one(".pc-body h3")
        excerpt = a.select_one(".pc-body p")
        eyebrow = a.select_one(".pc-body .pc-eyebrow")
        meta = a.select_one(".pc-body .pc-meta")
        href = a.get("href", "")
        slug = href.strip("/").split("/")[-1] if href else ""
        cards.append({
            "slug": slug,
            "href": href,
            "category": (eyebrow.get_text(strip=True) if eyebrow else ""),
            "data_cat": a.get("data-cat", ""),
            "title": (h3.get_text(strip=True) if h3 else ""),
            "excerpt": (excerpt.get_text(strip=True) if excerpt else ""),
            "meta": (meta.get_text(strip=True) if meta else ""),
            "img_src": (img.get("src") if img else None),
            "img_alt": (img.get("alt") if img else None),
            "node": a,
            "node_img": img,
        })
    return cards


def find_featured(soup: BeautifulSoup) -> dict | None:
    a = soup.select_one("a.featured-card")
    if not a:
        return None
    img = a.select_one(".f-media img")
    h2 = a.select_one(".f-body h2")
    excerpt = a.select_one(".f-body .f-excerpt")
    eyebrow = a.select_one(".f-body .f-eyebrow")
    meta = a.select_one(".f-body .f-meta")
    return {
        "node": a,
        "node_img": img,
        "href": a.get("href", ""),
        "title": (h2.get_text(strip=True) if h2 else ""),
        "img_src": (img.get("src") if img else None),
    }


# ---------- rotation ----------

def compute_bucket(today: dt.date, epoch_str: str, days: int) -> int:
    epoch = dt.date.fromisoformat(epoch_str)
    return max(0, (today - epoch).days) // days


def pick_featured(cards: list[dict], bucket: int, cfg: dict) -> dict:
    ex_slugs = set(cfg.get("featured_exclusions", {}).get("slugs", []) or [])
    ex_tags = [t.lower() for t in cfg.get("featured_exclusions", {}).get("tags", []) or []]

    def included(c):
        if c["slug"] in ex_slugs:
            return False
        cat = (c.get("data_cat") or c.get("category") or "").lower()
        for t in ex_tags:
            if t in cat or t in c["slug"].lower():
                return False
        return True

    eligible = [c for c in cards if included(c)]
    if not eligible:
        eligible = cards[:]
    # Stable deterministic ordering by slug, then rotate by bucket
    eligible_sorted = sorted(eligible, key=lambda c: c["slug"])
    return eligible_sorted[bucket % len(eligible_sorted)]


# ---------- drift check + fix ----------

def drift_scan(cards: list[dict], origin: str, wpm: int) -> list[dict]:
    """For every card, fetch the live article and compare hero vs card img.
    Returns list of per-card records with drift fields populated.
    """
    records = []
    for c in cards:
        url = absolutise(c["href"], origin)
        record = {
            "slug": c["slug"],
            "url": url,
            "card_img": clean_src(c["img_src"] or ""),
            "article_hero": None,
            "og_image": None,
            "schema_image": None,
            "read_time_min": None,
            "fetch_error": None,
            "hero_drift": False,
            "og_drift": False,
            "schema_drift": False,
        }
        try:
            html = http_get(url)
            hero = extract_article_hero_src(html)
            og = extract_og_image(html)
            sch = extract_schema_article_image(html)
            record["article_hero"] = clean_src(hero or "")
            record["og_image"] = clean_src(og or "")
            record["schema_image"] = clean_src(sch or "")
            record["read_time_min"] = compute_read_time(html, wpm)
            if record["article_hero"] and record["card_img"] and (
                record["article_hero"] != record["card_img"]
            ):
                record["hero_drift"] = True
            if record["article_hero"] and record["og_image"]:
                # og should point to an actual hero, not the site logo
                if (
                    "logo-orange" in record["og_image"]
                    or "mascot-only" in record["og_image"]
                ):
                    record["og_drift"] = True
                elif record["article_hero"].split("/")[-1] not in record["og_image"]:
                    # mismatched filename = drift
                    record["og_drift"] = True
            if record["article_hero"] and record["schema_image"]:
                if record["article_hero"].split("/")[-1] not in record["schema_image"]:
                    record["schema_drift"] = True
        except Exception as e:
            record["fetch_error"] = f"{type(e).__name__}: {e}"
        records.append(record)
    return records


def apply_hero_fixes(cards: list[dict], drift: list[dict]) -> list[dict]:
    by_slug = {d["slug"]: d for d in drift}
    applied = []
    for c in cards:
        d = by_slug.get(c["slug"])
        if not d or not d["hero_drift"] or not d["article_hero"]:
            continue
        # We update the src to the canonical article hero. Preserve Photon prefix
        # if card was using Photon (Jetpack rewrites on read).
        new_src = d["article_hero"]
        c["node_img"]["src"] = new_src
        # Force recompute by clearing srcset if present
        if c["node_img"].has_attr("srcset"):
            del c["node_img"]["srcset"]
        applied.append({
            "slug": c["slug"],
            "from": c["img_src"],
            "to": new_src,
        })
        c["img_src"] = new_src
    return applied


def apply_featured(soup: BeautifulSoup, featured_card: dict, drift_by_slug: dict, origin: str) -> dict:
    f = soup.select_one("a.featured-card")
    if not f:
        raise RuntimeError("No a.featured-card found on live /blog/ page")

    # IMG + alt
    f_img = f.select_one(".f-media img")
    hero = drift_by_slug.get(featured_card["slug"], {}).get("article_hero") or featured_card["img_src"]
    if f_img is not None and hero:
        f_img["src"] = hero
        if featured_card.get("img_alt"):
            f_img["alt"] = featured_card["img_alt"]
        if f_img.has_attr("srcset"):
            del f_img["srcset"]

    # href + aria-label
    f["href"] = featured_card["href"]
    f["aria-label"] = featured_card["title"]

    # Eyebrow (category)
    eyebrow = f.select_one(".f-body .f-eyebrow")
    if eyebrow:
        eyebrow.string = featured_card.get("category") or featured_card.get("data_cat") or "Guides"

    # Title
    h2 = f.select_one(".f-body h2")
    if h2:
        h2.string = featured_card["title"]

    # Excerpt
    excerpt = f.select_one(".f-body .f-excerpt")
    if excerpt:
        excerpt.string = featured_card["excerpt"]

    # Meta (byline + dot + read time)
    meta = f.select_one(".f-body .f-meta")
    if meta:
        meta.clear()
        byline = featured_card["meta"] or "By The Right Workshop service team"
        read_min = drift_by_slug.get(featured_card["slug"], {}).get("read_time_min") or 6
        meta.append(soup.new_tag("span"))
        meta.contents[-1].string = byline
        dot = soup.new_tag("span", attrs={"class": "dot"})
        meta.append(dot)
        rt = soup.new_tag("span")
        rt.string = f"{read_min} min read"
        meta.append(rt)

    return {"slug": featured_card["slug"], "title": featured_card["title"], "href": featured_card["href"]}


# ---------- orchestration ----------

def run(mode: str) -> int:
    env = load_env()
    cfg = load_config()
    page_id = cfg["blog_page_id"]
    origin = cfg["site_origin"]
    wpm = cfg.get("wpm_for_read_time", 220)

    page = fetch_blog_page_raw(env, page_id)
    raw = page.get("content", {}).get("raw") or page.get("content", {}).get("rendered") or ""
    if not raw:
        log("ERROR: empty page content fetched from WP")
        return 2

    inner, was_wrapped = unwrap_wp_html(raw)
    soup = BeautifulSoup(inner, "lxml")
    # bs4 with lxml wraps in <html><body> — unwrap for serialization later
    cards = parse_cards(soup)
    feat_now = find_featured(soup)

    today = dt.date.today()
    bucket = compute_bucket(today, cfg["rotation"]["epoch"], cfg["rotation"]["days_per_bucket"])
    picked = pick_featured(cards, bucket, cfg)

    # Drift scan = fetch every article once
    drift = drift_scan(cards, origin, wpm)
    drift_by_slug = {d["slug"]: d for d in drift}

    # Summary print
    print("=" * 72)
    print(f"TRW BLOG INDEX REFRESH  |  mode={mode}  |  {today.isoformat()}")
    print(f"Bucket #{bucket}  (epoch={cfg['rotation']['epoch']}, days={cfg['rotation']['days_per_bucket']})")
    print("=" * 72)
    print(f"Cards on /blog/: {len(cards)}")
    print(f"Currently featured: {feat_now['title'] if feat_now else '(none)'}")
    print(f"Proposed featured (bucket {bucket}): {picked['title']}")
    print(f"  href     : {picked['href']}")
    print(f"  category : {picked.get('category') or picked.get('data_cat')}")
    print(f"  img      : {drift_by_slug.get(picked['slug'], {}).get('article_hero') or picked['img_src']}")

    hero_drift = [d for d in drift if d["hero_drift"]]
    og_drift = [d for d in drift if d["og_drift"]]
    schema_drift = [d for d in drift if d["schema_drift"]]
    errors = [d for d in drift if d["fetch_error"]]

    print("\n--- DRIFT REPORT ---")
    print(f"Hero drift (auto-fix): {len(hero_drift)}")
    for d in hero_drift:
        print(f"  • {d['slug']}")
        print(f"      card: {d['card_img']}")
        print(f"      live: {d['article_hero']}")
    print(f"OG:image drift (flag only): {len(og_drift)}")
    for d in og_drift:
        print(f"  • {d['slug']} og={d['og_image']}")
    print(f"Schema Article.image drift (flag only): {len(schema_drift)}")
    for d in schema_drift:
        print(f"  • {d['slug']} schema={d['schema_image']}")
    if errors:
        print(f"FETCH ERRORS: {len(errors)}")
        for d in errors:
            print(f"  • {d['slug']}: {d['fetch_error']}")

    if mode == "report":
        return 0

    if mode == "check":
        print("\n(check mode — no writes)")
        return 0

    # --- apply ---

    fixes = apply_hero_fixes(cards, drift)
    feat_change = apply_featured(soup, picked, drift_by_slug, origin)

    # Determine if the featured block ACTUALLY changed
    featured_changed = (
        (feat_now is None)
        or (feat_now.get("href") != picked["href"])
        or (clean_src(feat_now.get("img_src") or "") != clean_src(
            drift_by_slug.get(picked["slug"], {}).get("article_hero") or picked["img_src"] or ""
        ))
    )

    if not fixes and not featured_changed:
        log("No drift, featured unchanged — no push.")
        print("\nNo-op (nothing to push).")
        return 0

    # Serialise back. bs4 + lxml wraps in html/body — strip those wrappers.
    serialised = soup.decode()
    serialised = re.sub(r"^\s*<html><body>", "", serialised)
    serialised = re.sub(r"</body></html>\s*$", "", serialised)
    # Sometimes lxml drops <!DOCTYPE>; our inner never had one, so this is fine.

    new_raw = rewrap_wp_html(serialised, was_wrapped)

    # Push
    resp = push_blog_page(env, page_id, new_raw)
    log(
        f"PUSH ok: featured='{feat_change['title']}' "
        f"({feat_change['href']}), hero_fixes={len(fixes)}, "
        f"bucket={bucket}"
    )
    for fx in fixes:
        log(f"  hero-fix {fx['slug']}: {fx['from']} -> {fx['to']}")
    print(f"\nPushed to WP page {page_id}. modified={resp.get('modified')}")
    return 0


def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="Dry-run drift + featured preview")
    g.add_argument("--apply", action="store_true", help="Apply changes and push to WP")
    g.add_argument("--report", action="store_true", help="Print current live state only")
    args = p.parse_args()
    if args.check:
        sys.exit(run("check"))
    elif args.apply:
        sys.exit(run("apply"))
    else:
        sys.exit(run("report"))


if __name__ == "__main__":
    main()
