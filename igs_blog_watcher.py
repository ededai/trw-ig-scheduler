#!/usr/bin/env python3
"""
TRW IGS blog watcher.

Polls therightworkshop.com/blog/ (parsed live, since TRW posts are stored as
raw HTML inside one WP page rather than standard WP posts). For each new post
detected (not in seen-state), renders 3 IGS variants (A/B/C) via igs_render.py
and queues them for the next 3 days at IGS slots.

Slot rules (per `feedback_trw_igs_posting_rules.md`):
  - Posting hours: any time, any day (no time-of-day cap)
  - Same-post spacing: 2 hours minimum between IGS for the same post
  - Different-post stacking: allowed
  - Reserved feed slots (12:30, 19:30, 21:00 SGT): never used for IGS

Variant rotation:
  - Day 1: Variant A (Editorial Teaser)
  - Day 2: Variant B (Question Hook)
  - Day 3: Variant C (Quote Pull)

Run hourly via GH Actions cron.
"""
import json
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup

SGT = ZoneInfo("Asia/Singapore")
ROOT = Path(__file__).parent.resolve()
SEEN_FILE = ROOT / "blog" / "igs_seen.json"
QUEUE_RUN = ROOT / "ig_queue.py"
RENDER = ROOT / "igs_render.py"
ASSETS_DIR = ROOT / "assets"
BLOG_INDEX_URL = "https://therightworkshop.com/blog/"
SITE_ORIGIN = "https://therightworkshop.com"

# Default IGS time-of-day per variant (SGT). Avoids reserved feed slots
# (12:30, 19:30, 21:00).
DEFAULT_VARIANT_TIME = {
    "A": (15, 30),  # day 1: mid-afternoon
    "B": (11, 0),   # day 2: late morning
    "C": (20, 0),   # day 3: post-dinner (between 19:30 and 21:00 feed slots)
}


def now_sgt() -> datetime:
    return datetime.now(SGT)


def load_seen() -> dict:
    if SEEN_FILE.exists():
        return json.loads(SEEN_FILE.read_text())
    return {"posts": {}}


def save_seen(seen: dict) -> None:
    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(json.dumps(seen, indent=2, ensure_ascii=False))


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "trw-igs-watcher/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def parse_blog_cards() -> list[dict]:
    """Return list of {slug, href, title, excerpt} for all post cards on /blog/."""
    soup = BeautifulSoup(fetch(BLOG_INDEX_URL), "html.parser")
    cards = []
    for a in soup.select(".post-grid a.post-card"):
        href = a.get("href", "")
        slug = href.strip("/").split("/")[-1] if href else ""
        if not slug:
            continue
        h3 = a.select_one(".pc-body h3")
        excerpt = a.select_one(".pc-body p")
        cards.append({
            "slug": slug,
            "href": urljoin(SITE_ORIGIN, href),
            "title": h3.get_text(strip=True) if h3 else "",
            "excerpt": excerpt.get_text(strip=True) if excerpt else "",
        })
    # Featured card (separate selector)
    feat = soup.select_one("a.featured-card")
    if feat:
        href = feat.get("href", "")
        slug = href.strip("/").split("/")[-1] if href else ""
        if slug and not any(c["slug"] == slug for c in cards):
            h2 = feat.select_one(".f-body h2")
            excerpt = feat.select_one(".f-body .f-excerpt")
            cards.insert(0, {
                "slug": slug,
                "href": urljoin(SITE_ORIGIN, href),
                "title": h2.get_text(strip=True) if h2 else "",
                "excerpt": excerpt.get_text(strip=True) if excerpt else "",
            })
    return cards


def first_two_sentences(text: str, max_chars: int = 180) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?])\s+", text)
    out = ""
    for part in parts:
        if len(out) + len(part) + 1 > max_chars:
            break
        out = (out + " " + part).strip()
    return out or text[:max_chars]


def queue_run(args: list[str]) -> None:
    cmd = [sys.executable, str(QUEUE_RUN), *args]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    print(res.stdout, end="")
    if res.returncode != 0:
        print(res.stderr, file=sys.stderr)
        raise RuntimeError(f"ig_queue.py failed: {res.returncode}")


def render_variant(blog_url: str, variant: str, title: str, sub: str,
                   out_path: Path, bg_image: Path | None = None) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, str(RENDER),
        "--blog-url", blog_url,
        "--variant", variant,
        "--title", title,
        "--sub", sub,
        "--output", str(out_path),
    ]
    if bg_image:
        cmd += ["--bg-image", str(bg_image)]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    print(res.stdout, end="")
    if res.returncode != 0:
        print(res.stderr, file=sys.stderr)
        raise RuntimeError(f"igs_render.py failed: {res.returncode}")


def compute_anchor_day() -> datetime:
    """Pick the first calendar day on which Variant A's slot is still in the future.
    All other variant slots are computed relative to this anchor day."""
    ah, am = DEFAULT_VARIANT_TIME["A"]
    today = now_sgt().replace(hour=ah, minute=am, second=0, microsecond=0)
    if today < now_sgt():
        today = today + timedelta(days=1)
    return today


def slot_for_variant(variant: str, day_offset: int, anchor_day: datetime) -> str:
    """Slot time = anchor_day + day_offset days, with variant's preferred hour:min."""
    h, m = DEFAULT_VARIANT_TIME[variant]
    target = (anchor_day + timedelta(days=day_offset)).replace(hour=h, minute=m, second=0, microsecond=0)
    return target.strftime("%Y-%m-%dT%H:%M")


def variants_for_post(card: dict) -> list[dict]:
    title = card["title"]
    excerpt = first_two_sentences(card["excerpt"], 180)
    sents = re.split(r"(?<=[.!?])\s+", excerpt)
    short = next((s for s in sents if 30 < len(s) < 110), "")
    quote = f'"{short}"' if short else f'"{title}"'
    return [
        {"variant": "A", "title": title,
         "sub": excerpt or "Read the full guide on our blog."},
        {"variant": "B", "title": _question_hook_for(title),
         "sub": excerpt[:160]},
        {"variant": "C", "title": quote,
         "sub": "From our latest guide."},
    ]


def _question_hook_for(title: str) -> str:
    base = title.split(":")[0].strip()
    return f"Wait, did you know this about {base.lower()}?"


def queue_post_igs(card: dict) -> list[str]:
    slug = card["slug"]
    blog_url = card["href"]
    variants = variants_for_post(card)
    queued = []
    asset_dir = ASSETS_DIR / f"igs-{slug}"
    asset_dir.mkdir(parents=True, exist_ok=True)
    bg_path = asset_dir / "blog_bg.png"
    captions_path = asset_dir / "caption.txt"
    captions_path.write_text("(IGS — caption ignored by Meta API for stories)\n")

    anchor = compute_anchor_day()
    for i, v in enumerate(variants):
        out_png = asset_dir / f"igs_{v['variant']}.png"
        render_variant(
            blog_url=blog_url,
            variant=v["variant"],
            title=v["title"],
            sub=v["sub"],
            out_path=out_png,
            bg_image=bg_path if bg_path.exists() else None,
        )
        if not bg_path.exists():
            sibling = out_png.parent / f"{out_png.stem}_bg.png"
            if sibling.exists():
                sibling.rename(bg_path)

        slot = slot_for_variant(v["variant"], day_offset=i, anchor_day=anchor)
        post_id = f"igs-{slug}-{v['variant'].lower()}-d{i+1}"
        queue_run([
            "add",
            "--id", post_id,
            "--slot", slot,
            "--type", "story",
            "--caption-file", str(captions_path.relative_to(ROOT)),
            "--images", str(out_png.relative_to(ROOT)),
            "--notes", f"IGS {v['variant']} for blog: {slug}",
        ])
        queued.append(post_id)
    return queued


def main():
    seen = load_seen()
    cards = parse_blog_cards()
    if not cards:
        print("watcher: no cards parsed (page structure changed?)", file=sys.stderr)
        return 1
    new = [c for c in cards if c["slug"] not in seen["posts"]]
    if not new:
        print(f"watcher: no new posts (checked {len(cards)})")
        return 0
    for card in reversed(new):  # oldest first
        print(f"NEW POST: {card['slug']}")
        try:
            queued = queue_post_igs(card)
            seen["posts"][card["slug"]] = {
                "queued_at": now_sgt().strftime("%Y-%m-%d %H:%M SGT"),
                "queued_ids": queued,
                "title": card["title"],
            }
            save_seen(seen)
        except Exception as e:
            print(f"ERR queueing {card['slug']}: {e}", file=sys.stderr)
            continue
    return 0


if __name__ == "__main__":
    sys.exit(main())
