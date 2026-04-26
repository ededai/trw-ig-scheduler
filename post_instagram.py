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
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import requests

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

# ── Image hosting ─────────────────────────────────────────────────────────────
# Primary: serve directly from this repo via raw.githubusercontent.com
#   (works only when the repo is PUBLIC — no upload needed, the asset is already
#    committed by the watcher/scheduler before publish time).
# Fallbacks: catbox.moe / 0x0.st / uguu.se (work from local Mac, blocked from
#   GH Actions IPs as of 2026-04-26).
UA = "Mozilla/5.0 (compatible; trw-ig-scheduler/1.0; +https://therightworkshop.com)"
GH_REPO_OWNER = os.environ.get("GH_REPO_OWNER", "ededai")
GH_REPO_NAME = os.environ.get("GH_REPO_NAME", "trw-ig-scheduler")
GH_REPO_REF = os.environ.get("GH_REPO_REF", "main")


def _repo_root():
    return Path(__file__).parent.resolve()


def _raw_github_url(image_path: str) -> str:
    """Map a path inside the repo to its raw.githubusercontent.com URL.
    Caller must ensure the file is committed and pushed before publish.
    """
    p = Path(image_path).resolve()
    rel = p.relative_to(_repo_root())
    return f"https://raw.githubusercontent.com/{GH_REPO_OWNER}/{GH_REPO_NAME}/{GH_REPO_REF}/{rel.as_posix()}"


def _verify_url_fetchable(url: str, timeout: int = 15) -> bool:
    """HEAD probe to confirm the URL serves an image (200 OK + image/* content-type)."""
    try:
        r = requests.head(url, timeout=timeout, allow_redirects=True, headers={"User-Agent": UA})
        ct = r.headers.get("content-type", "")
        return r.status_code == 200 and ct.startswith("image/")
    except Exception:
        return False


def _upload_raw_github(image_path):
    """Return the raw.githubusercontent.com URL for the file (no upload)."""
    url = _raw_github_url(image_path)
    if not _verify_url_fetchable(url):
        raise RuntimeError(f"raw.githubusercontent.com not reachable for {url} — repo may be private or asset not pushed yet")
    return url


def _upload_catbox(image_path):
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


def upload_image_to_host(image_path: str, imgbb_api_key: str = None) -> str:
    """Resolve a publicly-fetchable URL for the image that IG's media-fetcher accepts.
    Order:
      1. raw.githubusercontent.com (no upload — works only when repo is PUBLIC)
      2. catbox.moe / 0x0.st / uguu.se (fallback uploaders, work from local Mac)
    imgbb is excluded — its CDN rejects IG's fetcher (verified 2026-04-26).
    """
    print(f"Resolving image URL: {image_path}")
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
                print(f"Image hosted at: {url} (via {host_name}, attempt {attempt + 1})")
                return url
            except Exception as e:
                errors.append(f"{host_name} attempt {attempt + 1}: {type(e).__name__}: {e}")
                if attempts > 1:
                    time.sleep(3 * (attempt + 1))
    raise RuntimeError("All image hosts failed:\n  " + "\n  ".join(errors[-9:]))

# ── Instagram Graph API ───────────────────────────────────────────────────────
def create_media_container(ig_user_id: str, access_token: str, image_url: str,
                            caption: str, media_type: str = "IMAGE") -> str:
    """Step 1: Create a media container and return the container ID."""
    print("Creating media container...")
    params = {
        "access_token": access_token,
    }
    # Stories don't accept caption (caption is feed-only)
    if media_type != "STORIES":
        params["caption"] = caption
    if media_type == "IMAGE":
        params["image_url"] = image_url
    elif media_type == "REELS":
        params["video_url"] = image_url
        params["media_type"] = "REELS"
    elif media_type == "STORIES":
        params["image_url"] = image_url
        params["media_type"] = "STORIES"

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
    parser.add_argument("--caption", default="", help="Caption text (include hashtags). Ignored for stories.")
    parser.add_argument("--story", action="store_true", help="Publish as Instagram Story (9:16, no caption)")
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
        media_type = "STORIES" if args.story else "IMAGE"
    elif args.image:
        if not imgbb_api_key:
            print("ERROR: IMGBB_API_KEY required to upload local images. Add it to tools/.env")
            sys.exit(1)
        media_url = upload_image_to_host(args.image, imgbb_api_key)
        media_type = "STORIES" if args.story else "IMAGE"
    else:
        # Video
        if not imgbb_api_key:
            print("ERROR: IMGBB_API_KEY required to upload local videos. Add it to tools/.env")
            sys.exit(1)
        media_url = upload_image_to_host(args.video, imgbb_api_key)
        media_type = "REELS"

    container_id = create_media_container(ig_user_id, access_token, media_url, args.caption, media_type)

    if media_type in ("REELS", "STORIES"):
        wait_for_container(container_id, access_token)

    post_id = publish_container(ig_user_id, access_token, container_id)
    if media_type == "STORIES":
        print(f"\nStory published. ID: {post_id}")
    else:
        print(f"\nView post: https://www.instagram.com/p/{post_id}/")

if __name__ == "__main__":
    main()
