#!/usr/bin/env python3
"""Phase 1 collector — pull recent public posts for the watchlist via Apify.

Economical by design: small default resultsLimit, optional --accounts subset,
and a --dry-run that estimates cost without spending credit.

Usage:
  python3 collect.py --limit 5 --accounts revolcarzgarage_sg,ocd.singapore
  python3 collect.py --limit 8            # all active accounts
  python3 collect.py --dry-run           # show what would run, spend nothing

Output: data/raw_<UTC-date>.json   (list of normalised post dicts)
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
ACTOR = "apify~instagram-scraper"
RUN_SYNC = f"https://api.apify.com/v2/acts/{ACTOR}/run-sync-get-dataset-items"


def load_token():
    env = ROOT / ".env"
    for line in env.read_text().splitlines():
        if line.strip().startswith("APIFY_API_TOKEN"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("APIFY_API_TOKEN not found in .env")


def load_watchlist():
    wl = json.loads((HERE / "watchlist.json").read_text())
    return [a for a in wl["accounts"] if a.get("active", True)]


def normalise(item, category):
    """Pull just the fields we rank on, from the actor's post item."""
    return {
        "account": item.get("ownerUsername") or item.get("inputUrl", "").rstrip("/").split("/")[-1],
        "category": category,
        "url": item.get("url"),
        "type": item.get("type"),  # Image / Video / Sidecar(carousel)
        "caption": (item.get("caption") or "")[:600],
        "hashtags": item.get("hashtags", []),
        "likes": item.get("likesCount"),
        "comments": item.get("commentsCount"),
        "video_views": item.get("videoViewCount") or item.get("videoPlayCount"),
        "owner_followers": item.get("ownerFollowersCount"),
        "timestamp": item.get("timestamp"),
    }


def _run_actor(token, payload):
    req = urllib.request.Request(
        f"{RUN_SYNC}?token={token}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=600) as resp:
        return json.loads(resp.read())


def fetch_profiles(token, handles):
    """One details call for all accounts -> {handle: followersCount}."""
    urls = [f"https://www.instagram.com/{h}/" for h in handles]
    items = _run_actor(token, {"directUrls": urls, "resultsType": "details", "resultsLimit": 1})
    out = {}
    for it in items:
        u = it.get("username")
        if u:
            out[u] = it.get("followersCount")
    return out


def collect(handles_with_cat, limit, dry_run):
    token = load_token()
    urls = [f"https://www.instagram.com/{h}/" for h, _ in handles_with_cat]
    est = len(urls) * limit
    print(f"Accounts: {len(urls)} · limit/account: {limit} · est. results: ~{est}")
    if dry_run:
        print("DRY RUN — no credit spent. Accounts:")
        for h, c in handles_with_cat:
            print(f"  @{h}  ({c})")
        return []

    # Follower counts first (cheap details call), then posts.
    followers = fetch_profiles(token, [h for h, _ in handles_with_cat])

    payload = {
        "directUrls": urls,
        "resultsType": "posts",
        "resultsLimit": limit,
        "addParentData": True,   # attaches owner follower count to each post
        "searchType": "user",
    }
    req = urllib.request.Request(
        f"{RUN_SYNC}?token={token}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    cat_by_handle = {h: c for h, c in handles_with_cat}
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            items = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"Apify HTTP {e.code}: {e.read().decode()[:300]}")

    out = []
    for it in items:
        acct = it.get("ownerUsername", "")
        cat = cat_by_handle.get(acct, "unknown")
        row = normalise(it, cat)
        if row.get("owner_followers") is None:
            row["owner_followers"] = followers.get(acct)
        out.append(row)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=5, help="posts per account")
    ap.add_argument("--accounts", default="", help="comma-separated subset of handles")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    active = load_watchlist()
    if args.accounts:
        want = {a.strip() for a in args.accounts.split(",")}
        active = [a for a in active if a["handle"] in want]
    handles_with_cat = [(a["handle"], a["category"]) for a in active]

    rows = collect(handles_with_cat, args.limit, args.dry_run)
    if args.dry_run:
        return

    # Stamp date from the newest post we got (no Date.now in this env; use data)
    (HERE / "data").mkdir(exist_ok=True)
    out_path = HERE / "data" / "raw_latest.json"
    out_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False))
    print(f"\nCollected {len(rows)} posts -> {out_path}")
    # Quick shape check
    if rows:
        s = rows[0]
        print("Sample fields present:", {k: (v if k != 'caption' else (v or '')[:40]) for k, v in s.items() if k in ('account','type','likes','comments','video_views','owner_followers','timestamp')})


if __name__ == "__main__":
    main()
