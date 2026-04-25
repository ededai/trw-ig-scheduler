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
    if not ENV_FILE.exists():
        print(f"ERROR: .env not found at {ENV_FILE}")
        sys.exit(1)
    env = {}
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"')
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


def upload_to_imgbb(image_path, api_key=None):
    """Upload to catbox.moe (Instagram can fetch from it; imgbb blocks IG's crawler)."""
    import requests
    with open(image_path, "rb") as f:
        r = requests.post(
            "https://catbox.moe/user/api.php",
            data={"reqtype": "fileupload"},
            files={"fileToUpload": f},
            timeout=90,
        )
    r.raise_for_status()
    url = r.text.strip()
    if not url.startswith("http"):
        raise RuntimeError(f"catbox upload failed: {url}")
    return url


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
