#!/usr/bin/env python3
"""Auto-refresh topic_tags.json from WP REST `tags` taxonomy.

Bryan's pipeline (WP admin publish) doesn't write to topic_tags.json the
way Cole's cmd_publish_news_draft does. This script bridges the gap by
scanning WP for all published pages + their tags and updating the JSON.

Audit 2026-05-17 fix #5. Runs daily BEFORE sync_topic_pages.py so the
topic-page sync picks up new mappings.

Merge policy:
  - Existing entries in topic_tags.json preserved unless WP tags differ
  - Missing entries auto-added
  - Slugs starting with '_' (metadata keys) untouched
"""
from __future__ import annotations
import base64, json, os
from pathlib import Path
from urllib import request, error

WP_ORIGIN = "https://therightworkshop.com"
HERE = Path(__file__).parent
TOPIC_TAGS_PATH = HERE / "topic_tags.json"


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


def main() -> int:
    env = load_env()
    if not env.get("WORDPRESS_USERNAME"):
        print("ABORT: WP credentials missing"); return 1

    if not TOPIC_TAGS_PATH.exists():
        print(f"ABORT: {TOPIC_TAGS_PATH} not found"); return 1

    current = json.loads(TOPIC_TAGS_PATH.read_text())
    print(f"loaded topic_tags.json: {len(current)} entries")

    # WP tags taxonomy: build tag_id -> slug map
    tags = []
    for page_num in range(1, 4):
        rows = wp_get(env, "/tags", f"?per_page=100&page={page_num}&_fields=id,slug")
        if not rows: break
        tags.extend(rows)
    tag_by_id = {t["id"]: t["slug"] for t in tags}
    print(f"WP tag taxonomy: {len(tag_by_id)} tags")

    # WP pages: paginate all published with tags field
    pages: list[dict] = []
    for page_num in range(1, 6):
        rows = wp_get(env, "/pages",
                      f"?status=publish&per_page=100&page={page_num}&_fields=slug,tags,parent")
        if not rows: break
        pages.extend(rows)
    print(f"WP pages scanned: {len(pages)}")

    # Build slug -> [tag_slugs]
    discovered: dict[str, list[str]] = {}
    for p in pages:
        if p.get("parent"): continue  # skip topic children
        slug = p.get("slug") or ''
        if not slug or slug.startswith("_"): continue
        tag_ids = p.get("tags") or []
        if not tag_ids: continue
        tag_slugs = sorted(set(tag_by_id.get(tid) for tid in tag_ids if tag_by_id.get(tid)))
        if tag_slugs:
            discovered[slug] = tag_slugs

    # Merge: add new entries; update existing entries whose tag sets differ
    added = 0
    updated = 0
    for slug, tag_slugs in discovered.items():
        existing = current.get(slug)
        if existing is None:
            current[slug] = tag_slugs
            added += 1
        elif sorted(existing) != tag_slugs:
            current[slug] = tag_slugs
            updated += 1

    if added == 0 and updated == 0:
        print("topic_tags.json: no changes needed.")
        return 0

    TOPIC_TAGS_PATH.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")
    print(f"topic_tags.json: added={added} updated={updated} total={len(current)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
