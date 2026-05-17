#!/usr/bin/env python3
"""Daily defensive sweep: refresh every post-card's <p>excerpt</p> on every
hub from the article's WP excerpt field (single source of truth).

Cron-friendly. Lives in trw-ig-scheduler/blog/ so it runs on cloud cron
with no trw-cole/wp-import dependency. Idempotent.
"""
from __future__ import annotations
import base64, html as html_mod, json, os, re
from pathlib import Path
from urllib import request, error

WP_ORIGIN = "https://therightworkshop.com"
HERE = Path(__file__).parent
TOPICS_PARENT_ID = 1597
HUB_PAGES = [
    (475,  '/blog/'),
    (1776, '/news/'),
    (1772, '/guides/'),
    (1774, '/car-tips/'),
    (1597, '/topics/'),
]


def load_env() -> dict:
    env = {}
    for k in ("WORDPRESS_USERNAME", "WORDPRESS_PASSWORD"):
        if os.environ.get(k):
            env[k] = os.environ[k]
    if len(env) == 2:
        return env
    for cand in [
        Path("/Users/admin/the-right-workshop/tools/.env"),
        HERE.parent / "tools" / ".env",
        Path(".env"),
    ]:
        if cand.exists():
            for line in cand.read_text().splitlines():
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            break
    return env


def auth_header(env: dict) -> str:
    return "Basic " + base64.b64encode(
        f"{env['WORDPRESS_USERNAME']}:{env['WORDPRESS_PASSWORD']}".encode()
    ).decode()


def wp_get(env: dict, path: str, params: str = ""):
    url = f"{WP_ORIGIN}/wp-json/wp/v2{path}{params}"
    req = request.Request(url, headers={"Authorization": auth_header(env)})
    try:
        with request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except error.HTTPError as e:
        if e.code == 400: return None
        print(f"  GET {path} -> HTTP {e.code}")
        return None


def wp_push(env: dict, page_id: int, content: str) -> bool:
    url = f"{WP_ORIGIN}/wp-json/wp/v2/pages/{page_id}"
    body = json.dumps({"content": content}).encode()
    req = request.Request(
        url, data=body, method="POST",
        headers={"Authorization": auth_header(env), "Content-Type": "application/json"},
    )
    try:
        with request.urlopen(req, timeout=60) as r:
            r.read(); return True
    except error.HTTPError as e:
        print(f"  POST {page_id} -> HTTP {e.code}: {e.read().decode()[:200]}")
        return False


def esc(s: str) -> str:
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def main() -> int:
    env = load_env()
    if not env.get("WORDPRESS_USERNAME"):
        print("ABORT: WP credentials missing"); return 1

    print("Building slug -> excerpt cache...")
    slug_excerpt: dict[str, str] = {}
    for page_num in range(1, 6):
        rows = wp_get(env, "/pages",
                      f"?status=publish&per_page=100&page={page_num}&_fields=id,slug,excerpt,parent")
        if not rows: break
        for r in rows:
            if r.get('parent'): continue
            slug = r.get('slug') or ''
            raw_ex = ((r.get('excerpt') or {}).get('rendered') or '').strip()
            clean = html_mod.unescape(re.sub(r'<[^>]+>', '', raw_ex)).strip()
            if clean:
                slug_excerpt[slug] = clean[:200]
    print(f"  cached {len(slug_excerpt)} article excerpts")

    topic_children = wp_get(env, "/pages", f"?parent={TOPICS_PARENT_ID}&per_page=100&_fields=id,slug") or []
    hub_pages = list(HUB_PAGES)
    for c in topic_children:
        hub_pages.append((c["id"], f"/topics/{c['slug']}/"))

    refreshed_total = 0
    for hub_pid, hub_label in hub_pages:
        page = wp_get(env, f"/pages/{hub_pid}", "?context=edit&_fields=content")
        if not page: continue
        raw = (page.get("content") or {}).get("raw", "") or ""
        if not raw: continue
        cards_replaced = [0]

        def repl(m):
            full = m.group(0)
            href = m.group(1)
            slug_match = re.search(r'/([a-z0-9][a-z0-9-]+)/?$', href)
            if not slug_match: return full
            slug = slug_match.group(1)
            clean = slug_excerpt.get(slug)
            if not clean: return full
            new_full, n = re.subn(r'<p>[\s\S]*?</p>',
                                  f'<p>{esc(clean)[:200]}</p>',
                                  full, count=1)
            if n == 1 and new_full != full:
                cards_replaced[0] += 1
                return new_full
            return full

        new = re.sub(r'<a[^>]+class="post-card"[^>]+href="([^"]+)"[^>]*>[\s\S]*?</a>',
                     repl, raw)
        if new == raw: continue
        if wp_push(env, hub_pid, new):
            print(f"  {hub_pid:>5} {hub_label:38} refreshed {cards_replaced[0]} cards")
            refreshed_total += cards_replaced[0]

    print(f"\nTotal cards refreshed: {refreshed_total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
