#!/usr/bin/env python3
"""Phase 1 ranker — score collected posts by engagement rate + velocity.

Reads data/raw_latest.json, writes data/ranked_latest.json and prints a
human-readable top-N table.

Two signals, combined:
  engagement_rate = (likes + 2*comments) / followers     # comments weighted 2x
  velocity        = (likes + 2*comments) / days_since_post
  score           = normalised(engagement_rate) + normalised(velocity)

Velocity catches fresh winners; rate normalises across account sizes.
Saves/shares are not public per-post via this actor, so likes+comments proxy.

Usage:
  python3 rank.py --top 10
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "data" / "raw_latest.json"
WATCHLIST = HERE / "watchlist.json"


def days_since(ts):
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - dt
        return max(delta.total_seconds() / 86400, 0.25)  # floor at 6h
    except Exception:
        return None


def engagement(row):
    likes = row.get("likes") or 0
    comments = row.get("comments") or 0
    return likes + 2 * comments


def score_rows(rows):
    scored = []
    for r in rows:
        eng = engagement(r)
        followers = r.get("owner_followers") or 0
        d = days_since(r.get("timestamp"))
        rate = (eng / followers) if followers else 0.0
        velocity = (eng / d) if d else 0.0
        scored.append({**r, "engagement": eng, "engagement_rate": rate, "velocity": velocity, "days_old": round(d, 1) if d else None})

    # Normalise each signal 0..1 across the set, then sum.
    def norm(key):
        vals = [s[key] for s in scored if s[key] is not None]
        hi = max(vals) if vals else 0
        for s in scored:
            s[f"_n_{key}"] = (s[key] / hi) if hi else 0

    norm("engagement_rate")
    norm("velocity")
    for s in scored:
        s["score"] = round(s["_n_engagement_rate"] + s["_n_velocity"], 4)
    scored.sort(key=lambda s: s["score"], reverse=True)
    return scored


def apply_recency(rows, window_days):
    """Keep only posts within the recency window; report account dormancy."""
    fresh, dropped_old = [], 0
    newest_by_acct = {}
    for r in rows:
        d = days_since(r.get("timestamp"))
        acct = r.get("account")
        if d is not None and (acct not in newest_by_acct or d < newest_by_acct[acct]):
            newest_by_acct[acct] = d
        if d is not None and d <= window_days:
            fresh.append(r)
        else:
            dropped_old += 1
    return fresh, dropped_old, newest_by_acct


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--all", action="store_true", help="ignore recency window")
    args = ap.parse_args()

    wl = json.loads(WATCHLIST.read_text())
    window = wl.get("recency_window_days", 60)
    dormancy = wl.get("dormancy_days", 90)

    rows = json.loads(RAW.read_text())
    if not args.all:
        rows, dropped_old, newest_by_acct = apply_recency(rows, window)
        dormant = [a for a, d in newest_by_acct.items() if d > dormancy]
        print(f"Recency window: {window}d · dropped {dropped_old} older posts.")
        if dormant:
            print(f"DORMANT (newest post > {dormancy}d, consider cutting): {', '.join('@'+a for a in dormant)}")
        print()
    scored = score_rows(rows)

    out = HERE / "data" / "ranked_latest.json"
    out.write_text(json.dumps(scored, indent=2, ensure_ascii=False))

    print(f"Ranked {len(scored)} posts. Top {args.top}:\n")
    print(f"{'#':>2}  {'score':>5}  {'acct':<20} {'type':<8} {'eng':>6} {'foll':>7} {'age':>5}  caption")
    for i, s in enumerate(scored[:args.top], 1):
        cap = (s.get("caption") or "").replace("\n", " ")[:46]
        foll = s.get("owner_followers")
        print(f"{i:>2}  {s['score']:>5.2f}  @{s['account']:<19} {str(s.get('type')):<8} {s['engagement']:>6} {str(foll):>7} {str(s.get('days_old')):>5}  {cap}")


if __name__ == "__main__":
    main()
