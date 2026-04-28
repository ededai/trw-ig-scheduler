#!/usr/bin/env python3
"""IGS auto-fill — back-fill all free IGS slots over the next 14 days
with random blog post variants (A / B / C).

Picks blog posts at random with a "no-recent-repeat" guard. Renders each
IGS PNG via igs_render.py and queues it via ig_queue.py.

Slot times (SGT): 11:00 (B), 15:30 (A), 20:00 (C). Variant is locked
to the slot per memory `feedback_trw_igs_posting_rules.md` to keep the
A/B/C cadence consistent — A=15:30, B=11:00, C=20:00.

Usage:
  python3 igs_autofill.py [--days 14] [--start 2026-04-29] [--dry-run]
"""
import argparse, json, random, subprocess, sys
from pathlib import Path
from datetime import date, datetime, timedelta

ROOT = Path(__file__).parent
QUEUE_FILE = ROOT / "ig_queue.json"
SEEN_FILE = ROOT / "blog" / "igs_seen.json"
ASSETS_DIR = ROOT / "assets"
IGS_RENDER = ROOT / "igs_render.py"
TRW_BLOG_BASE = "https://www.therightworkshop.com/blog/"

# Slot -> variant (per existing IGS rule)
SLOT_VARIANT = {"11:00": "B", "15:30": "A", "20:00": "C"}

# Variant title prefixes (renderer uses VARIANT_CONFIG eyebrow)
# Title = blog post title, sub = teaser CTA
SUB_BY_VARIANT = {
    "A": "Read the full guide on the blog.",
    "B": "Tap link in bio for the full read.",
    "C": "Save this for your next service.",
}


def load_queue() -> dict:
    return json.loads(QUEUE_FILE.read_text())


def load_blog_posts() -> dict:
    data = json.loads(SEEN_FILE.read_text())
    return data["posts"]  # slug -> {title, ...}


def free_igs_slots(start: date, days: int) -> list:
    """Return list of (date_str, time_str, variant) tuples for free IGS slots."""
    q = load_queue()
    booked = set()
    for e in q.get("pending", []) + q.get("posted", []) + q.get("failed", []):
        slot = e.get("slot_time_sgt", "")
        if e.get("type") == "story":
            booked.add(slot)
    free = []
    for d in range(days):
        cur = start + timedelta(days=d)
        for time_str, variant in SLOT_VARIANT.items():
            slot = f"{cur}T{time_str}"
            if slot not in booked:
                free.append((str(cur), time_str, variant))
    return free


def pick_blog_post(posts: dict, recent_slugs: list) -> str:
    """Pick a slug avoiding the last few used."""
    candidates = [s for s in posts if s not in recent_slugs[-5:]]
    if not candidates:
        candidates = list(posts)
    return random.choice(candidates)


def render_one(blog_slug: str, blog_title: str, variant: str, slot_id: str) -> Path:
    """Render an IGS PNG for the given blog + variant. Returns the PNG path."""
    asset_dir = ASSETS_DIR / slot_id
    asset_dir.mkdir(exist_ok=True, parents=True)
    out_png = asset_dir / "story.png"
    blog_url = f"{TRW_BLOG_BASE}{blog_slug}/"
    cmd = [
        sys.executable, str(IGS_RENDER),
        "--blog-url", blog_url,
        "--variant", variant,
        "--title", blog_title,
        "--sub", SUB_BY_VARIANT[variant],
        "--output", str(out_png),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        print(f"    render FAIL: {r.stderr[-200:]}")
        return None
    # Caption — IGS doesn't display caption but ig_queue.py requires the file
    caption = asset_dir / "caption.txt"
    caption.write_text(f"Auto-filled IGS for blog: {blog_slug} (variant {variant})")
    return out_png


def queue_entry(slug: str, slot: str, png: Path, caption: Path, blog_slug: str, variant: str):
    cmd = [
        sys.executable, str(ROOT / "ig_queue.py"), "add",
        "--id", slug,
        "--slot", slot,
        "--type", "story",
        "--caption-file", str(caption.relative_to(ROOT)),
        "--images", str(png.relative_to(ROOT)),
        "--notes", f"Auto-fill IGS — blog:{blog_slug} variant:{variant}",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--start", default=str(date.today()))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d").date()
    posts = load_blog_posts()
    free = free_igs_slots(start, args.days)
    print(f"Free IGS slots in next {args.days} days: {len(free)}")

    if args.dry_run:
        for d, t, v in free:
            print(f"  {d}T{t} — variant {v}")
        return

    random.seed(20260428)
    recent = []
    queued = 0
    for d, t, v in free:
        slug = pick_blog_post(posts, recent)
        recent.append(slug)
        title = posts[slug]["title"]
        slot_id = f"igs-autofill-{slug[:30]}-{d}-{t.replace(':','')}"
        slot = f"{d}T{t}"
        print(f"  {slot} [{v}] -> {slug[:40]} :: {title[:50]}")
        png = render_one(slug, title, v, slot_id)
        if not png or not png.exists():
            print(f"    skip — no png")
            continue
        caption = png.parent / "caption.txt"
        if queue_entry(slot_id, slot, png, caption, slug, v):
            queued += 1
        else:
            print(f"    queue add FAIL")
    print(f"\nQueued {queued} / {len(free)} IGS slots.")


if __name__ == "__main__":
    main()
