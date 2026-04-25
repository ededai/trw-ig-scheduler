#!/usr/bin/env python3
"""
Instagram posting tool for The Right Workshop.
Uses the Meta Graph API to publish photos and videos.

Usage:
  python3 post_instagram.py --image path/to/photo.jpg --caption "Your caption"
  python3 post_instagram.py --video path/to/video.mp4 --caption "Your caption"
  python3 post_instagram.py --url "https://..." --caption "Your caption"
"""

import argparse
import os
import sys
import json
import time
import subprocess
import requests
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
ENV_FILE = Path(__file__).parent / ".env"

def load_env():
    """Load credentials. .env file when present (local dev), os.environ otherwise (GH Actions)."""
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                env[key.strip()] = val.strip().strip('"')
    for key in ("IG_USER_ID", "IG_ACCESS_TOKEN", "IMGBB_API_KEY"):
        if not env.get(key) and os.environ.get(key):
            env[key] = os.environ[key]
    if not env.get("IG_USER_ID") or not env.get("IG_ACCESS_TOKEN"):
        print("ERROR: IG_USER_ID and IG_ACCESS_TOKEN must be set (.env file or environment).")
        sys.exit(1)
    return env

# ── Image hosting (imgbb — free, no account needed for small files) ───────────
def upload_image_to_host(image_path: str, imgbb_api_key: str) -> str:
    """Upload a local image to imgbb and return the public URL."""
    print(f"Uploading image: {image_path}")
    with open(image_path, "rb") as f:
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            params={"key": imgbb_api_key},
            files={"image": f},
            timeout=60,
        )
    response.raise_for_status()
    data = response.json()
    url = data["data"]["url"]
    print(f"Image hosted at: {url}")
    return url

# ── Instagram Graph API ───────────────────────────────────────────────────────
def create_media_container(ig_user_id: str, access_token: str, image_url: str,
                            caption: str, media_type: str = "IMAGE") -> str:
    """Step 1: Create a media container and return the container ID."""
    print("Creating media container...")
    params = {
        "access_token": access_token,
        "caption": caption,
    }
    if media_type == "IMAGE":
        params["image_url"] = image_url
    elif media_type == "REELS":
        params["video_url"] = image_url
        params["media_type"] = "REELS"

    response = requests.post(
        f"https://graph.facebook.com/v19.0/{ig_user_id}/media",
        params=params,
        timeout=60,
    )
    data = response.json()
    if "error" in data:
        print(f"ERROR creating container: {data['error']['message']}")
        sys.exit(1)
    container_id = data["id"]
    print(f"Container created: {container_id}")
    return container_id

def wait_for_container(container_id: str, access_token: str, max_wait: int = 120):
    """Poll until the media container is ready (important for videos)."""
    print("Waiting for container to be ready...")
    for _ in range(max_wait // 5):
        response = requests.get(
            f"https://graph.facebook.com/v19.0/{container_id}",
            params={"fields": "status_code", "access_token": access_token},
            timeout=30,
        )
        status = response.json().get("status_code", "")
        if status == "FINISHED":
            print("Container ready.")
            return
        if status == "ERROR":
            print("ERROR: Container processing failed.")
            sys.exit(1)
        print(f"  Status: {status} — waiting...")
        time.sleep(5)
    print("ERROR: Timed out waiting for container.")
    sys.exit(1)

def publish_container(ig_user_id: str, access_token: str, container_id: str) -> str:
    """Step 2: Publish the container and return the post ID."""
    print("Publishing post...")
    response = requests.post(
        f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish",
        params={"creation_id": container_id, "access_token": access_token},
        timeout=60,
    )
    data = response.json()
    if "error" in data:
        print(f"ERROR publishing: {data['error']['message']}")
        sys.exit(1)
    post_id = data["id"]
    print(f"SUCCESS! Post published. ID: {post_id}")
    return post_id

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Post to The Right Workshop Instagram")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--image", help="Path to a local image file")
    group.add_argument("--video", help="Path to a local video file (posted as Reel)")
    group.add_argument("--url", help="Publicly accessible image URL")
    parser.add_argument("--caption", required=True, help="Caption text (include hashtags)")
    parser.add_argument("--dry-run", action="store_true", help="Print caption without posting")
    args = parser.parse_args()

    if args.dry_run:
        print("=== DRY RUN ===")
        print("Caption:")
        print(args.caption)
        return

    env = load_env()
    ig_user_id = env.get("IG_USER_ID")
    access_token = env.get("IG_ACCESS_TOKEN")
    imgbb_api_key = env.get("IMGBB_API_KEY", "")

    if not ig_user_id or not access_token:
        print("ERROR: IG_USER_ID and IG_ACCESS_TOKEN must be set in tools/.env")
        sys.exit(1)

    # Determine media URL and type
    if args.url:
        media_url = args.url
        media_type = "IMAGE"
    elif args.image:
        if not imgbb_api_key:
            print("ERROR: IMGBB_API_KEY required to upload local images. Add it to tools/.env")
            sys.exit(1)
        media_url = upload_image_to_host(args.image, imgbb_api_key)
        media_type = "IMAGE"
    else:
        # Video
        if not imgbb_api_key:
            print("ERROR: IMGBB_API_KEY required to upload local videos. Add it to tools/.env")
            sys.exit(1)
        media_url = upload_image_to_host(args.video, imgbb_api_key)
        media_type = "REELS"

    container_id = create_media_container(ig_user_id, access_token, media_url, args.caption, media_type)

    if media_type == "REELS":
        wait_for_container(container_id, access_token)

    post_id = publish_container(ig_user_id, access_token, container_id)
    print(f"\nView post: https://www.instagram.com/p/{post_id}/")

if __name__ == "__main__":
    main()
