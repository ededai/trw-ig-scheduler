#!/usr/bin/env python3
"""
Duplicate-post guard for @therightworkshop Instagram.

Call check_duplicate(caption, env) before ANY post attempt.
It checks two layers:
  1. Local ig_post_log.md  (fast, catches same-session repeats)
  2. Live IG Graph API     (catches cross-system dupes: GH Actions vs manual)

Raises SystemExit(1) on a detected duplicate unless force=True.
"""

import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

TOOLS = Path(__file__).parent
POST_LOG = TOOLS / "ig_post_log.md"
QUEUE_FILE = TOOLS / "ig_queue.json"
LOOKBACK_HOURS = 72  # check the last 3 days on IG


def _caption_key(caption: str) -> str:
    return caption.strip()[:80].lower()


def _check_local_log(key: str) -> None:
    if not POST_LOG.exists():
        return
    for line in POST_LOG.read_text().splitlines():
        if not line.startswith("|") or "---" in line or "Caption headline" in line:
            continue
        cols = [c.strip() for c in line.split("|")]
        if len(cols) >= 4:
            headline = cols[3].strip()
            if headline and key[:40] and headline.lower()[:40] == key[:40]:
                print(f"\nDUPLICATE GUARD (local log): '{headline}'")
                print("This caption was already posted. Use --force to override.")
                raise SystemExit(1)


def _check_queue_posted(key: str) -> None:
    if not QUEUE_FILE.exists():
        return
    try:
        q = json.loads(QUEUE_FILE.read_text())
    except (json.JSONDecodeError, ValueError):
        return
    for entry in q.get("posted", []):
        cf = entry.get("caption_file", "")
        if cf and Path(cf).exists():
            try:
                posted_key = _caption_key(Path(cf).read_text())
                if posted_key[:40] and key[:40] == posted_key[:40]:
                    print(f"\nDUPLICATE GUARD (queue posted): entry '{entry['id']}' posted {entry.get('posted_at','?')}")
                    print("Use --force to override.")
                    raise SystemExit(1)
            except OSError:
                pass


def _check_live_ig(key: str, env: dict) -> None:
    token = env.get("IG_ACCESS_TOKEN", "")
    user_id = env.get("IG_USER_ID", "")
    if not token or not user_id:
        return

    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    url = (
        f"https://graph.facebook.com/v19.0/{user_id}/media"
        f"?fields=id,timestamp,caption&limit=30"
        f"&access_token={urllib.parse.quote(token)}"
    )
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.load(r)
    except Exception as exc:
        print(f"WARN: ig_post_guard live-check failed ({exc}) — proceeding without live guard")
        return

    for post in data.get("data", []):
        raw_ts = post.get("timestamp", "")
        if not raw_ts:
            continue
        ts = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
        if ts < cutoff:
            continue
        posted_cap = post.get("caption", "")
        if not posted_cap:
            continue
        posted_key = _caption_key(posted_cap)
        if key[:50] and posted_key[:50] == key[:50]:
            print(f"\nDUPLICATE GUARD (live IG): already posted {ts.strftime('%Y-%m-%d %H:%M SGT')}")
            print(f"  https://www.instagram.com/p/{post['id']}/")
            print("Use --force to override.")
            raise SystemExit(1)


def check_duplicate(caption: str, env: dict | None = None, force: bool = False) -> None:
    """
    Run all duplicate checks. Call this before any IG publish call.
    Pass force=True to skip all checks (emergency override).
    """
    if force:
        print("ig_post_guard: --force passed, skipping duplicate checks.")
        return

    key = _caption_key(caption)
    _check_local_log(key)
    _check_queue_posted(key)
    if env:
        _check_live_ig(key, env)
