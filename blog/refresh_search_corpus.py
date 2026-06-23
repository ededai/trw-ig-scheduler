#!/usr/bin/env python3
"""Refresh the TRW site-search corpus + JS on every search-bearing page.

Single source of truth for the live search. Runs daily in GitHub Actions
(after sync_blog_hub_posts has added any new post cards) and can also be run
once by hand to repair drift. Idempotent — no-op when nothing changed.

What it does, per page that carries the canonical `.trw-search` component:
  1. Rebuilds `window.TRW_SEARCH_CORPUS` with a `k` (keywords) field per post,
     keywords sourced from topic_tags.json tags + search_keyword_overrides.json.
  2. Replaces the search init <script> with the canonical fixed version from
     trw_search.build_search_bar (tokenised keyword matching + Enter-to-top-result).
  3. Preserves the page's existing data-scope and chip label exactly.

Master article list = the post-cards currently on /blog/ (page 475), which the
daily sync_blog_hub_posts step keeps fresh. So a newly published article becomes
searchable automatically on the next cron run — no manual step.

Targets:
  475   /blog/            scope=blog        corpus = all articles
  1597  /topics/          scope=tags        corpus = all articles
  <N>   /topics/{tag}/    scope=tag-archive corpus = articles carrying that tag
        (children of 1597; tag pages with no posts have no search block — skipped)

/news/ (1776) carries a different legacy search widget and is handled separately.

Usage:
  python3 refresh_search_corpus.py            # dry-run: report what would change
  python3 refresh_search_corpus.py --apply    # push changes to WP
"""
from __future__ import annotations
import argparse, base64, json, os, re, sys, html
from pathlib import Path
from urllib import request, error

try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("bs4 required: pip install beautifulsoup4 lxml")

import trw_search as T

HERE = Path(__file__).resolve().parent
WP_ORIGIN = "https://therightworkshop.com"
BLOG_PAGE_ID = 475
TOPICS_HUB_ID = 1597
TOPIC_TAGS_PATH = HERE / "topic_tags.json"

# Derive the canonical corpus + init <script> tags and the rank patterns from
# the verified build_search_bar (single source of truth — never hand-typed).
_SAMPLE = T.build_search_bar([], "tag-archive", "X")
_INIT_SCRIPT = re.search(r'(<script>\(function\(\)\{.*\}\)\(\);</script>)\s*$', _SAMPLE, re.S).group(1)
_NEW_RANK = re.search(r'(function rank\(q\)\{.*?return t0\.concat\(t1\)\.concat\(t2\)\})', _SAMPLE, re.S).group(1)
# Old (broken) rank that may still be live on un-migrated pages.
_OLD_RANK_RE = re.compile(
    r'function rank\(q\)\{q=q\.trim\(\)\.toLowerCase\(\);if\(!q\)return \[\];var s=\[\],c=\[\];.*?return s\.concat\(c\)\}',
    re.S,
)
_CORPUS_ASSIGN_RE = re.compile(r'window\.TRW_SEARCH_CORPUS\s*=\s*\[.*?\]\s*;', re.S)
_SEARCH_SECTION_RE = re.compile(r'<section class="trw-search-section">.*?</section>', re.S)


def _corpus_script(corpus):
    return "<script>window.TRW_SEARCH_CORPUS=" + json.dumps(corpus, ensure_ascii=False) + ";</script>"


def load_env() -> dict:
    """Credentials from GH Actions secrets (env) or local tools/.env."""
    env = {k: os.environ[k] for k in ("WORDPRESS_USERNAME", "WORDPRESS_PASSWORD") if k in os.environ}
    if "WORDPRESS_USERNAME" in env and "WORDPRESS_PASSWORD" in env:
        return env
    p = Path("/Users/admin/the-right-workshop/tools/.env")
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                v = v.strip()
                if (v[:1] == '"' and v[-1:] == '"') or (v[:1] == "'" and v[-1:] == "'"):
                    v = v[1:-1]
                env[k.strip()] = v
    if "WORDPRESS_USERNAME" not in env or "WORDPRESS_PASSWORD" not in env:
        sys.exit("Missing WORDPRESS_USERNAME / WORDPRESS_PASSWORD")
    return env


def _auth(env):
    return base64.b64encode(f"{env['WORDPRESS_USERNAME']}:{env['WORDPRESS_PASSWORD']}".encode()).decode()


def wp_get(env, path):
    req = request.Request(f"{WP_ORIGIN}/wp-json/wp/v2{path}", headers={"Authorization": f"Basic {_auth(env)}"})
    with request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def wp_post(env, path, body):
    data = json.dumps(body).encode()
    req = request.Request(f"{WP_ORIGIN}/wp-json/wp/v2{path}", data=data, method="POST",
                          headers={"Authorization": f"Basic {_auth(env)}", "Content-Type": "application/json"})
    try:
        with request.urlopen(req, timeout=180) as r:
            return json.loads(r.read().decode())
    except error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.read().decode()[:300]}")
        return None


def get_raw(env, pid):
    return (wp_get(env, f"/pages/{pid}?context=edit&_fields=content") or {}).get("content", {}).get("raw", "") or ""


def clean(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def load_topic_tags():
    d = json.loads(TOPIC_TAGS_PATH.read_text())
    return {k: v for k, v in d.items() if not k.startswith("_")}


def parse_blog_cards(blog_raw):
    """Master article list from /blog/ post-cards: [(slug, title)] in page order."""
    soup = BeautifulSoup(blog_raw, "html.parser")
    out, seen = [], set()
    for a in soup.select("a.post-card"):
        href = a.get("href", "")
        m = re.match(r"^/([^/]+)/$", href)
        if not m:
            continue
        slug = m.group(1)
        if slug in seen:
            continue
        h3 = a.find("h3")
        title = clean(h3.get_text()) if h3 else slug
        seen.add(slug)
        out.append((slug, title))
    return out


def extract_scope_chip(block):
    scope_m = re.search(r'data-scope="([^"]+)"', block)
    chip_m = re.search(r'<span class="trw-search-chip">(?:<svg.*?</svg>)?\s*([^<]*?)\s*</span>', block, re.S)
    scope = scope_m.group(1) if scope_m else "blog"
    chip = html.unescape(chip_m.group(1)) if chip_m else "All Posts"
    return scope, chip


def build_master(env):
    """Return ordered list of corpus items {n,u,k} for all live /blog/ articles."""
    tags_by_slug = load_topic_tags()
    overrides = T.load_keyword_overrides()
    cards = parse_blog_cards(get_raw(env, BLOG_PAGE_ID))
    if not cards:
        sys.exit("No post-cards found on /blog/ — aborting (refusing to write an empty corpus).")
    master = []
    for slug, title in cards:
        master.append({
            "item": T.corpus_item(slug, title, tags_by_slug.get(slug, []), overrides),
            "slug": slug,
            "tags": tags_by_slug.get(slug, []),
        })
    return master, tags_by_slug


def corpus_for(master, tag=None):
    if tag is None:
        return [m["item"] for m in master]
    return [m["item"] for m in master if tag in (m["tags"] or [])]


def _build_new_raw(raw, corpus):
    """Return (new_raw, mode) applying the safest transform for this page's shape.

    Path 1 (clean block: section+corpus+init adjacent) -> atomic block replace.
    Path 2 (corpus+init present but split across wp:html comments) -> in-place
            corpus swap + rank swap + Enter swap (never crosses a block boundary).
    Path 3 (search section shell only, no corpus/JS) -> insert corpus+init
            scripts right after the section, inside its existing wp:html block.
    Returns (None, reason) when there is nothing to do.
    """
    # Path 1
    m = T.SEARCH_BLOCK_RE.search(raw)
    if m:
        scope, chip = extract_scope_chip(m.group(0))
        new_block = T.build_search_bar(corpus, scope, chip)
        return (raw[:m.start()] + new_block + raw[m.end():], "block")
    # Path 2: corpus + init exist, just split by wp:html comments
    if "TRW_SEARCH_CORPUS" in raw and "function rank(q)" in raw:
        new = _CORPUS_ASSIGN_RE.sub(
            lambda _m: "window.TRW_SEARCH_CORPUS=" + json.dumps(corpus, ensure_ascii=False) + ";", raw, count=1)
        new = _OLD_RANK_RE.sub(lambda _m: _NEW_RANK, new, count=1)
        new = new.replace(
            'else if(items.length===1){e.preventDefault();window.location.href=items[0].getAttribute("href")}',
            'else if(items.length){e.preventDefault();window.location.href=items[0].getAttribute("href")}', 1)
        return (new, "inplace")
    # Path 3: section HTML present but no scripts — inject scripts after the section
    sm = _SEARCH_SECTION_RE.search(raw)
    if sm and "TRW_SEARCH_CORPUS" not in raw:
        scripts = _corpus_script(corpus) + _INIT_SCRIPT
        return (raw[:sm.end()] + scripts + raw[sm.end():], "inject")
    # Path 4: tag archive that has the search CSS but never rendered the search
    # HTML at all (newer "Posts tagged X" template). Inject the full component
    # above the post grid, inside its single wp:html block. Chip from <span class="tag-name">.
    if ".trw-search-section{" in raw and '<section class="trw-search-section">' not in raw:
        grid = raw.find('<section class="post-grid-section">')
        tn = re.search(r'<span class="tag-name">([^<]+)</span>', raw)
        if grid != -1 and tn:
            block = T.build_search_bar(corpus, "tag-archive", "In " + html.unescape(tn.group(1)))
            anchor = raw.rfind('<!-- POST GRID -->', 0, grid)
            ins = anchor if anchor != -1 else grid
            return (raw[:ins] + block + "\n\n" + raw[ins:], "inject-full")
    return (None, "no-search")


def refresh_page(env, pid, label, corpus, apply):
    raw = get_raw(env, pid)
    if not raw:
        print(f"  SKIP {label} ({pid}): no content")
        return False
    new_raw, mode = _build_new_raw(raw, corpus)
    if new_raw is None:
        print(f"  SKIP {label} ({pid}): {mode}")
        return False
    if new_raw == raw:
        print(f"  OK   {label} ({pid}): already current ({len(corpus)} items, {mode})")
        return False
    print(f"  CHG  {label} ({pid}): {len(corpus)} items [{mode}]")
    if apply:
        r = wp_post(env, f"/pages/{pid}", {"content": new_raw})
        print("       pushed." if r else "       PUSH FAILED.")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="push changes (default: dry-run)")
    args = ap.parse_args()
    env = load_env()

    master, tags_by_slug = build_master(env)
    print(f"Master article list: {len(master)} posts from /blog/.")
    all_corpus = corpus_for(master)

    changed = 0
    changed += refresh_page(env, BLOG_PAGE_ID, "/blog/", all_corpus, args.apply)
    changed += refresh_page(env, TOPICS_HUB_ID, "/topics/", all_corpus, args.apply)

    tag_pages = wp_get(env, f"/pages?parent={TOPICS_HUB_ID}&per_page=100&_fields=id,slug")
    for tp in sorted(tag_pages, key=lambda p: p["slug"]):
        scoped = corpus_for(master, tag=tp["slug"])
        if not scoped:
            print(f"  SKIP /topics/{tp['slug']}/ ({tp['id']}): 0 posts for tag")
            continue
        changed += refresh_page(env, tp["id"], f"/topics/{tp['slug']}/", scoped, args.apply)

    mode = "APPLIED" if args.apply else "DRY-RUN (no writes)"
    print(f"\n{mode}: {changed} page(s) {'changed' if args.apply else 'would change'}.")


if __name__ == "__main__":
    main()
