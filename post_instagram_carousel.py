#!/usr/bin/env python3
"""
Instagram carousel posting tool for The Right Workshop.
Uses the Meta Graph API (same creds as post_instagram.py) to publish
a multi-image carousel (2-10 slides).

Usage:
  python3 post_instagram_carousel.py \\
    --images slide_01.png slide_02.png ... slide_07.png \\
    --caption-file caption.txt \\
    [--dry-run]
"""

import argparse
import sys
import time
import urllib.parse
import urllib.request
import json
from pathlib import Path

ENV_FILE = Path(__file__).parent / ".env"


def load_env():
    """Load credentials. .env file when present (local dev), os.environ otherwise (GH Actions)."""
    import os
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip('"')
    # Always fall back to / overlay environ — works on GH Actions where secrets are env vars.
    for key in ("IG_USER_ID", "IG_ACCESS_TOKEN", "IMGBB_API_KEY"):
        if not env.get(key) and os.environ.get(key):
            env[key] = os.environ[key]
    if not env.get("IG_USER_ID") or not env.get("IG_ACCESS_TOKEN"):
        print("ERROR: IG_USER_ID and IG_ACCESS_TOKEN must be set (.env file or environment).")
        sys.exit(1)
    return env


def http_post(url, params, files=None):
    import requests
    if files:
        r = requests.post(url, params=params, files=files, timeout=120)
    else:
        r = requests.post(url, params=params, timeout=180)
    r.raise_for_status()
    return r.json()


def http_get(url, params):
    import requests
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


UA = "Mozilla/5.0 (compatible; trw-ig-scheduler/1.0; +https://therightworkshop.com)"


def _upload_catbox(image_path):
    import requests
    with open(image_path, "rb") as f:
        r = requests.post(
            "https://catbox.moe/user/api.php",
            data={"reqtype": "fileupload"},
            files={"fileToUpload": f},
            headers={"User-Agent": UA},
            timeout=120,
        )
    r.raise_for_status()
    url = r.text.strip()
    if not url.startswith("http"):
        raise RuntimeError(f"catbox bad response: {url[:200]}")
    return url


def _upload_0x0(image_path):
    import requests
    with open(image_path, "rb") as f:
        r = requests.post(
            "https://0x0.st",
            files={"file": f},
            headers={"User-Agent": UA},
            timeout=120,
        )
    r.raise_for_status()
    url = r.text.strip()
    if not url.startswith("http"):
        raise RuntimeError(f"0x0 bad response: {url[:200]}")
    return url


def _upload_uguu(image_path):
    import requests
    with open(image_path, "rb") as f:
        r = requests.post(
            "https://uguu.se/upload?output=text",
            files={"files[]": f},
            headers={"User-Agent": UA},
            timeout=120,
        )
    r.raise_for_status()
    url = r.text.strip().split()[0]
    if not url.startswith("http"):
        raise RuntimeError(f"uguu bad response: {url[:200]}")
    return url


import os as _os

GH_REPO_OWNER = _os.environ.get("GH_REPO_OWNER", "ededai")
GH_REPO_NAME = _os.environ.get("GH_REPO_NAME", "trw-ig-scheduler")
GH_REPO_REF = _os.environ.get("GH_REPO_REF", "main")


def _raw_github_url(image_path):
    p = Path(image_path).resolve()
    rel = p.relative_to(Path(__file__).parent.resolve())
    return f"https://raw.githubusercontent.com/{GH_REPO_OWNER}/{GH_REPO_NAME}/{GH_REPO_REF}/{rel.as_posix()}"


def _upload_raw_github(image_path):
    import requests
    url = _raw_github_url(image_path)
    try:
        r = requests.head(url, timeout=15, allow_redirects=True,
                          headers={"User-Agent": "trw-ig-scheduler/1.0"})
    except Exception as e:
        raise RuntimeError(f"raw.github HEAD failed: {e}")
    if r.status_code != 200 or not r.headers.get("content-type", "").startswith("image/"):
        raise RuntimeError(
            f"raw.github not serving image (status={r.status_code}, ct={r.headers.get('content-type','?')}); "
            "is the repo public and the asset committed/pushed?"
        )
    return url


def upload_to_imgbb(image_path, api_key=None):
    """Resolve a publicly-fetchable URL for the image.
    Order:
      1. raw.githubusercontent.com (no upload — works only when repo is PUBLIC)
      2. catbox.moe / 0x0.st / uguu.se (fallback uploaders, work from local Mac)
    Function name kept for back-compat; imgbb itself is not used (its CDN
    rejects IG's fetcher per 2026-04-26 verification).
    """
    import time
    hosts = [
        ("raw.githubusercontent.com", _upload_raw_github),
        ("catbox.moe", _upload_catbox),
        ("0x0.st", _upload_0x0),
        ("uguu.se", _upload_uguu),
    ]
    errors = []
    for host_name, fn in hosts:
        attempts = 1 if host_name == "raw.githubusercontent.com" else 3
        for attempt in range(attempts):
            try:
                url = fn(image_path)
                print(f"[upload] {host_name} succeeded on attempt {attempt + 1}")
                return url
            except Exception as e:
                errors.append(f"{host_name} attempt {attempt + 1}: {type(e).__name__}: {e}")
                if attempts > 1:
                    time.sleep(3 * (attempt + 1))
    raise RuntimeError("All image hosts failed:\n  " + "\n  ".join(errors[-9:]))


def create_child_container(ig_user_id, token, image_url):
    """Create a child media container for a carousel slide."""
    data = http_post(
        f"https://graph.facebook.com/v19.0/{ig_user_id}/media",
        {
            "access_token": token,
            "image_url": image_url,
            "is_carousel_item": "true",
        },
    )
    if "error" in data:
        raise RuntimeError(f"Child container error: {data['error']}")
    return data["id"]


def create_carousel_container(ig_user_id, token, child_ids, caption):
    """Create the parent carousel container referencing all children."""
    data = http_post(
        f"https://graph.facebook.com/v19.0/{ig_user_id}/media",
        {
            "access_token": token,
            "media_type": "CAROUSEL",
            "children": ",".join(child_ids),
            "caption": caption,
        },
    )
    if "error" in data:
        raise RuntimeError(f"Carousel container error: {data['error']}")
    return data["id"]


def wait_ready(container_id, token, max_wait=180):
    for _ in range(max_wait // 5):
        data = http_get(
            f"https://graph.facebook.com/v19.0/{container_id}",
            {"fields": "status_code", "access_token": token},
        )
        status = data.get("status_code", "")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise RuntimeError(f"Container {container_id} processing failed")
        time.sleep(5)
    raise RuntimeError(f"Timed out waiting for {container_id}")


def publish(ig_user_id, token, container_id):
    data = http_post(
        f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish",
        {"creation_id": container_id, "access_token": token},
    )
    if "error" in data:
        raise RuntimeError(f"Publish error: {data['error']}")
    return data["id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", nargs="+", required=True, help="2-10 image paths in order")
    ap.add_argument("--caption-file", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    images = [Path(p).expanduser().resolve() for p in args.images]
    if not (2 <= len(images) <= 10):
        print(f"ERROR: carousel needs 2-10 images, got {len(images)}")
        sys.exit(1)
    for p in images:
        if not p.exists():
            print(f"ERROR: missing image {p}")
            sys.exit(1)

    caption = Path(args.caption_file).read_text().strip()

    if args.dry_run:
        print("=== DRY RUN ===")
        print(f"Images ({len(images)}):")
        for i, p in enumerate(images, 1):
            print(f"  {i}. {p}")
        print("\nCaption:")
        print(caption)
        return

    env = load_env()
    ig_user_id = env.get("IG_USER_ID")
    token = env.get("IG_ACCESS_TOKEN")
    if not ig_user_id or not token:
        print("ERROR: IG_USER_ID and IG_ACCESS_TOKEN required in .env")
        sys.exit(1)

    print(f"Uploading {len(images)} images to catbox.moe...")
    urls = []
    for i, p in enumerate(images, 1):
        u = upload_to_imgbb(str(p))
        urls.append(u)
        print(f"  {i}/{len(images)}: {u}")

    print("Creating child containers...")
    child_ids = []
    for i, u in enumerate(urls, 1):
        cid = create_child_container(ig_user_id, token, u)
        child_ids.append(cid)
        print(f"  {i}/{len(urls)}: {cid}")

    print("Creating carousel container...")
    parent = create_carousel_container(ig_user_id, token, child_ids, caption)
    print(f"  parent: {parent}")

    print("Waiting for carousel container to be ready...")
    wait_ready(parent, token)

    print("Publishing carousel...")
    post_id = publish(ig_user_id, token, parent)
    print(f"\nSUCCESS. Post id: {post_id}")
    print(f"View: https://www.instagram.com/p/{post_id}/")


if __name__ == "__main__":
    main()
