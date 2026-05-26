#!/usr/bin/env python3
"""
Generate a branded featured image and set it on a TRW WordPress post/page.

Renders a news card using news_card_renderer.py (pure Pillow, no browser),
uploads it to WP media, and sets featured_media on the target post/page.

Usage (CLI):
  python3 generate_and_upload_featured.py \
      --post-id 7557 \
      --card-type lta \
      --label "SINGAPORE LTA UPDATE" \
      --headline "Revised ERP rates from 2 June 2026" \
      --stat "$1 rise during school holidays"

  # Also publish the post in the same call:
  python3 generate_and_upload_featured.py ... --publish

Environment (loaded from .env or inherited from GitHub Actions secrets):
  WORDPRESS_API_URL    https://therightworkshop.com/wp-json/wp/v2
  WORDPRESS_USERNAME   therightworkshoppteltd
  WORDPRESS_PASSWORD   "app password"
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import tempfile
from pathlib import Path
from urllib import request, error

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from news_card_renderer import render_news_card  # type: ignore


# ── env helpers ───────────────────────────────────────────────────────────────

def _load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    for key in ("WORDPRESS_API_URL", "WORDPRESS_USERNAME", "WORDPRESS_PASSWORD"):
        val = (os.environ.get(key) or "").strip()
        if not val:
            # .env fallback (local dev)
            env_file = HERE.parent / ".env"
            if env_file.exists():
                for line in env_file.read_text().splitlines():
                    line = line.strip()
                    if line.startswith(key + "="):
                        val = line[len(key) + 1:].strip().strip('"').strip("'")
                        break
        env[key] = val
    missing = [k for k, v in env.items() if not v]
    if missing:
        print(f"[error] Missing env vars: {missing}", file=sys.stderr)
        sys.exit(1)
    return env


def _api_base(env: dict) -> str:
    """Return the WP REST API v2 base URL, e.g. https://therightworkshop.com/wp-json/wp/v2"""
    url = env["WORDPRESS_API_URL"].rstrip("/")
    if not url.endswith("/wp/v2"):
        url = url.rstrip("/wp-json").rstrip("/") + "/wp-json/wp/v2"
    return url


def _auth(env: dict) -> str:
    token = base64.b64encode(
        f"{env['WORDPRESS_USERNAME']}:{env['WORDPRESS_PASSWORD']}".encode()
    ).decode()
    return f"Basic {token}"


# ── WP API calls ──────────────────────────────────────────────────────────────

def _upload_media(api: str, auth: str, image_path: Path, slug: str) -> int:
    filename = f"{slug}.png"
    boundary = "----TRWBoundary7MA4YWxkTrZu0gW"
    with open(image_path, "rb") as f:
        img_data = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: image/png\r\n\r\n"
    ).encode() + img_data + f"\r\n--{boundary}--\r\n".encode()

    req = request.Request(
        f"{api}/media",
        data=body,
        headers={
            "Authorization": auth,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=60) as r:
            result = json.loads(r.read())
        media_id = result["id"]
        media_url = result.get("source_url", "")
        print(f"[upload] media_id={media_id}  url={media_url}")
        return media_id
    except error.HTTPError as e:
        print(f"[error] Media upload failed HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


def _set_featured_media(api: str, auth: str, post_type: str, post_id: int, media_id: int) -> None:
    url = f"{api}/{post_type}s/{post_id}"
    body = json.dumps({"featured_media": media_id}).encode()
    req = request.Request(
        url,
        data=body,
        headers={
            "Authorization": auth,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=30) as r:
            result = json.loads(r.read())
        fm = result.get("featured_media", "?")
        print(f"[wp] featured_media set to {fm} on {post_type}/{post_id}")
    except error.HTTPError as e:
        print(f"[error] Set featured_media failed HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


def _publish_post(api: str, auth: str, post_type: str, post_id: int) -> None:
    url = f"{api}/{post_type}s/{post_id}"
    body = json.dumps({"status": "publish"}).encode()
    req = request.Request(
        url,
        data=body,
        headers={
            "Authorization": auth,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=30) as r:
            result = json.loads(r.read())
        status = result.get("status", "?")
        link = result.get("link", "")
        print(f"[wp] status={status}  link={link}")
    except error.HTTPError as e:
        print(f"[error] Publish failed HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--post-id",   required=True, type=int, help="WP page/post ID")
    p.add_argument("--post-type", default="page", choices=["page", "post"], help="WP object type")
    p.add_argument("--card-type", default="lta",  choices=["coe", "lta"], help="Card template")
    p.add_argument("--label",     required=True,  help="Eyebrow label, e.g. 'SINGAPORE LTA UPDATE'")
    p.add_argument("--headline",  required=True,  help="Main article headline")
    p.add_argument("--stat",      required=True,  help="Orange stat line, e.g. '$1 rise from 2 Jun'")
    p.add_argument("--publish",   action="store_true", help="Also publish the post after setting image")
    p.add_argument("--out",       default=None,   help="Save rendered PNG here too (optional)")
    return p.parse_args()


def main() -> None:
    args = _parse()
    env  = _load_env()
    api  = _api_base(env)
    auth = _auth(env)

    # Derive a filename slug from the headline
    import re
    slug = re.sub(r"[^a-z0-9]+", "-", args.headline.lower()).strip("-")[:60]
    slug = f"{args.card_type}_{slug}"

    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / f"{slug}.png"

        print(f"[render] card_type={args.card_type}  label={args.label!r}")
        print(f"         headline={args.headline!r}   stat={args.stat!r}")
        render_news_card(
            card_type=args.card_type,
            label=args.label,
            headline=args.headline,
            stat=args.stat,
            out_path=str(out_path),
        )
        print(f"[render] saved to {out_path}  ({out_path.stat().st_size // 1024} KB)")

        if args.out:
            import shutil
            shutil.copy(out_path, args.out)
            print(f"[render] also copied to {args.out}")

        media_id = _upload_media(api, auth, out_path, slug)
        _set_featured_media(api, auth, args.post_type, args.post_id, media_id)

        if args.publish:
            _publish_post(api, auth, args.post_type, args.post_id)

    print(f"[done] media_id={media_id}")


if __name__ == "__main__":
    main()
