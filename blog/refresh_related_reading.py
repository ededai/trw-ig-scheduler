#!/usr/bin/env python3
"""Refresh the [trw_related_reads] engine registry from the live site.

Single source of truth for the related-reading POOL + topic pillars. Runs daily in
GitHub Actions (after sync_blog_hub_posts has added any new article cards to /blog/)
and can be run by hand to deploy or repair. Idempotent — no-op when nothing changed.

What it does:
  1. Builds $REG = { page_id => [pillar slugs] } from the live /blog/ (page 475)
     article cards + topic_tags.json. A newly published article on /blog/ enters the
     registry automatically — no manual step.
  2. Deploys / updates Code Snippets snippet 52 ([trw_related_reads]):
       - first run (or --full): POST the whole v2 engine file with $REG injected.
       - thereafter: swap ONLY the block between RR_REGISTRY_START / RR_REGISTRY_END.
     Engine logic (related-first scoring, variants, render) is never touched by the
     recurring sync — only the data block moves.

Targets one snippet; the shortcode itself is already placed on every blog article and
(after rollout) every service page.

Usage:
  python3 refresh_related_reading.py            # dry-run: report what would change
  python3 refresh_related_reading.py --apply    # write to WP
  python3 refresh_related_reading.py --apply --full   # force full engine redeploy
"""
from __future__ import annotations
import argparse, base64, json, os, re, sys
from pathlib import Path
from urllib import request, error

HERE = Path(__file__).resolve().parent
WP_ORIGIN = "https://therightworkshop.com"
BLOG_PAGE_ID = 475
SNIPPET_ID = 52
TOPIC_TAGS_PATH = HERE / "topic_tags.json"
ENGINE_PATH = HERE / "trw_related_reading_snippet.php"
REG_START = "// RR_REGISTRY_START"
REG_END = "// RR_REGISTRY_END"


def load_env() -> dict:
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


def http(env, method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Authorization": f"Basic {_auth(env)}"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = request.Request(url, data=data, method=method, headers=headers)
    try:
        with request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode())
    except error.HTTPError as e:
        print(f"  HTTP {e.code} {method} {url}: {e.read().decode()[:300]}")
        return None


def wp_get(env, path):
    return http(env, "GET", f"{WP_ORIGIN}/wp-json/wp/v2{path}")


def cs_get(env, sid):
    return http(env, "GET", f"{WP_ORIGIN}/wp-json/code-snippets/v1/snippets/{sid}")


def cs_put(env, sid, fields):
    return http(env, "POST", f"{WP_ORIGIN}/wp-json/code-snippets/v1/snippets/{sid}", fields)


def get_raw(env, pid):
    return (wp_get(env, f"/pages/{pid}?context=edit&_fields=content") or {}).get("content", {}).get("raw", "") or ""


def load_topic_tags():
    d = json.loads(TOPIC_TAGS_PATH.read_text())
    return {k: v for k, v in d.items() if not k.startswith("_")}


def slug_to_id(env, slug):
    arr = wp_get(env, f"/pages?slug={slug}&_fields=id&status=publish")
    if isinstance(arr, list) and arr:
        return int(arr[0]["id"])
    return None


def id_to_slug(env, pid):
    o = wp_get(env, f"/pages/{pid}?_fields=slug")
    return (o or {}).get("slug")


def existing_ids(code):
    """Article IDs already in the snippet (v2 $REG keys or legacy $pool array ints)."""
    m = re.search(re.escape(REG_START) + r"(.*?)" + re.escape(REG_END), code, re.S)
    if m:
        return set(int(x) for x in re.findall(r"(\d+)\s*=>", m.group(1)))
    m = re.search(r"\$pool\s*=\s*array\(([^)]*)\)", code, re.S)
    if m:
        return set(int(x) for x in re.findall(r"\d+", m.group(1)))
    return set()


def build_registry(env, seed_ids):
    """Registry = topic_tags articles (slug->pillars, resolved to id) UNION any seed_ids
    (current snippet pool) so nothing currently shown is ever dropped. New articles flow in
    via topic_tags.json (kept fresh by cron step 5b)."""
    tags = load_topic_tags()
    reg, missing_tags, missing_id = {}, [], []
    # 1. topic_tags slugs (the maintained article set with pillars)
    for slug, pillars in tags.items():
        pid = slug_to_id(env, slug)
        if not pid:
            missing_id.append(slug)
            continue
        reg[pid] = list(pillars)
    # 2. preserve any currently-pooled IDs not covered above
    for pid in seed_ids:
        if pid in reg:
            continue
        slug = id_to_slug(env, pid)
        pillars = tags.get(slug, []) if slug else []
        if not pillars:
            missing_tags.append(slug or str(pid))
        reg[pid] = list(pillars)
    return reg, sorted(reg), missing_tags, missing_id


def reg_php(reg):
    lines = ["    $REG = array("]
    for pid in sorted(reg):
        pil = ", ".join("'" + p + "'" for p in reg[pid])
        lines.append(f"        {pid} => array({pil}),")
    lines.append("    );")
    return "\n".join(lines)


def inject_registry(engine_code, reg_block):
    """Replace the lines between the markers (inclusive of their inner content)."""
    pat = re.compile(re.escape(REG_START) + r".*?" + re.escape(REG_END), re.S)
    repl = REG_START + "\n" + reg_block + "\n    " + REG_END
    if not pat.search(engine_code):
        sys.exit("Engine has no RR_REGISTRY markers — aborting.")
    return pat.sub(lambda _m: repl, engine_code, count=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write to WP (default: dry-run)")
    ap.add_argument("--full", action="store_true", help="force full engine redeploy")
    args = ap.parse_args()
    env = load_env()

    snip = cs_get(env, SNIPPET_ID)
    if not snip:
        sys.exit(f"Could not GET snippet {SNIPPET_ID}.")
    cur_code = snip.get("code", "")
    seed = existing_ids(cur_code)

    reg, ids, missing_tags, missing_id = build_registry(env, seed)
    print(f"Registry: {len(reg)} articles (topic_tags + {len(seed)} seed pool IDs preserved).")
    if missing_id:
        print(f"  WARN topic_tags slug->id unresolved (skipped): {missing_id}")
    if missing_tags:
        print(f"  note: no pillars (random-fill only): {missing_tags}")
    reg_block = reg_php(reg)
    is_v2 = "RR_REGISTRY_START" in cur_code and "rr-svc-grid" in cur_code

    if args.full or not is_v2:
        engine = ENGINE_PATH.read_text()
        new_code = inject_registry(engine, reg_block)
        action = "FULL ENGINE DEPLOY" + ("" if is_v2 else " (snippet is pre-v2)")
    else:
        new_code = inject_registry(cur_code, reg_block)
        action = "registry sync"

    try:
        Path("/tmp/snippet52_v2.emit.php").write_text("<?php\n" + new_code)
    except Exception:
        pass
    if new_code == cur_code:
        print(f"  OK: snippet {SNIPPET_ID} already current ({action}). No write.")
        return
    print(f"  CHG: snippet {SNIPPET_ID} [{action}] — {len(cur_code)} -> {len(new_code)} chars")
    if args.apply:
        fields = {"code": new_code, "active": True, "scope": snip.get("scope", "front-end")}
        r = cs_put(env, SNIPPET_ID, fields)
        if r:
            print(f"       pushed. active={r.get('active')} code_len={len(r.get('code',''))}")
        else:
            print("       PUSH FAILED.")
    else:
        print("  DRY-RUN: pass --apply to write.")


if __name__ == "__main__":
    main()
