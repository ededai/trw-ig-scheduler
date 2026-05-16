#!/usr/bin/env python3
"""remap_article_topic_chips.py — rewrite each article's <div class="tags-row">
to hold the v3 pillar chips per topic_tags.json.

Strips dead links (any chip pointing to a slug not in slug_remap.json or
mapped to null). Adds missing pillar chips. Idempotent.

Usage:
  python3 remap_article_topic_chips.py --dry-run
  python3 remap_article_topic_chips.py
"""
from __future__ import annotations
import argparse, base64, json, os, re, sys
from pathlib import Path
from urllib import request, error

WP_ORIGIN = "https://therightworkshop.com"
HERE = Path(__file__).parent
TOPIC_TAGS_PATH = HERE / "topic_tags.json"

PILLAR_DISPLAY = {
    "aircon": "Aircon", "servicing": "Servicing", "tyres": "Tyres", "battery": "Battery",
    "brakes": "Brakes", "coolant": "Coolant", "suspension": "Suspension", "engine": "Engine",
    "gearbox": "Gearbox", "electrical": "Electrical", "accident-repair": "Accident Repair",
    "car-insurance": "Car Insurance", "coe": "COE", "scrap-or-export": "Scrap or Export",
    "used-car": "Used Car", "selling-your-car": "Selling Your Car", "ownership": "Ownership",
    "erp": "ERP", "regulation": "Regulation", "ev": "EV", "driving-tips": "Driving Tips",
    "workshop": "Workshop",
}

def load_env():
    env = {}
    for key in ("WORDPRESS_USERNAME", "WORDPRESS_PASSWORD", "WORDPRESS_API_URL"):
        if os.environ.get(key):
            env[key] = os.environ[key]
    if len(env) == 3:
        return env
    for c in [Path("/Users/admin/the-right-workshop/tools/.env"), HERE.parent / "tools" / ".env"]:
        if c.exists():
            for line in c.read_text().splitlines():
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            break
    return env

def auth_header(env):
    creds = f"{env['WORDPRESS_USERNAME']}:{env['WORDPRESS_PASSWORD']}"
    return "Basic " + base64.b64encode(creds.encode()).decode()

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
    body = json.dumps({"content": content}).encode()
    headers = {"Authorization": auth_header(env), "Content-Type": "application/json"}
    req = request.Request(url, data=body, method="POST", headers=headers)
    try:
        with request.urlopen(req, timeout=60) as r:
            r.read()
            return True
    except error.HTTPError as e:
        print(f"  PUSH {page_id} -> HTTP {e.code}: {e.read().decode()[:200]}")
        return False

def build_chip_block(pillars):
    chips = []
    for p in pillars:
        name = PILLAR_DISPLAY.get(p, p.replace('-', ' ').title())
        chips.append(f'<a href="/topics/{p}/" class="tag-chip">{name}</a>')
    return '<div class="tags-row">\n  ' + '\n  '.join(chips) + '\n</div>'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    dry = args.dry_run

    env = load_env()
    if not env.get("WORDPRESS_USERNAME"):
        sys.exit("ERROR: WP credentials missing")

    topic_tags = json.loads(TOPIC_TAGS_PATH.read_text())
    articles = {k: v for k, v in topic_tags.items() if not k.startswith("_") and isinstance(v, list)}

    print(f"Articles to process: {len(articles)}")

    pushed, skipped_unchanged, skipped_no_block, failed = 0, 0, 0, 0

    for slug, pillars in articles.items():
        pages = wp_get(env, "/pages", f"?slug={slug}&context=edit&_fields=id,content")
        if not pages:
            print(f"  ✗ /{slug}/ — not found")
            failed += 1
            continue
        page = pages[0]
        pid, raw = page["id"], page.get("content", {}).get("raw", "")

        # Find <div class="tags-row">...</div>
        m = re.search(r'<div class="tags-row">[\s\S]*?</div>', raw)
        if not m:
            print(f"  - /{slug}/ ({pid}) — no .tags-row block, skipping")
            skipped_no_block += 1
            continue

        old_block = m.group(0)
        new_block = build_chip_block(pillars)

        if old_block == new_block:
            skipped_unchanged += 1
            continue

        new_raw = raw.replace(old_block, new_block)

        # Verify the replacement actually changed something
        if new_raw == raw:
            print(f"  ✗ /{slug}/ ({pid}) — replacement no-op (str escaped?)")
            failed += 1
            continue

        if dry:
            print(f"  [DRY] /{slug}/ ({pid}):")
            print(f"        OLD: {old_block[:200]}")
            print(f"        NEW: {new_block[:200]}")
        else:
            if wp_push(env, pid, new_raw):
                print(f"  ✓ /{slug}/ ({pid}) -> {pillars}")
                pushed += 1
            else:
                failed += 1

    mode = "DRY-RUN" if dry else "LIVE"
    print(f"\n{mode} summary: pushed={pushed} unchanged={skipped_unchanged} no-block={skipped_no_block} failed={failed}")

if __name__ == "__main__":
    main()
