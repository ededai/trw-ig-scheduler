#!/usr/bin/env python3
"""
TRW Instagram Queue Runner — GitHub Actions edition.

Same semantics as the original tools/ig_queue.py, but path-portable so it
runs identically on Ed's Mac and on a GH Actions ubuntu-latest runner.

Path rules
  caption_file / image_paths can be:
    - absolute paths (used as-is)
    - relative paths (resolved against this script's directory, i.e. the
      repo root when running in GH Actions)

Subcommands: run, list, add, remove (see add --help).

Schema, grace window, and behaviour are identical to the original. See the
SKILL.md (~/.claude/skills/trw-ig-scheduler/SKILL.md) for full docs.
"""

import argparse
import fcntl
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

SGT = ZoneInfo("Asia/Singapore")
ROOT = Path(__file__).parent.resolve()
QUEUE_FILE = ROOT / "ig_queue.json"
LOCK_FILE = ROOT / ".ig_queue.lock"
LOG_DIR = ROOT / "logs"
RUN_LOG = LOG_DIR / "cron_ig.log"
POST_LOG_MD = ROOT / "ig_post_log.md"
POST_SINGLE = ROOT / "post_instagram.py"
POST_CAROUSEL = ROOT / "post_instagram_carousel.py"
GRACE_MINUTES = 90


def now_sgt() -> datetime:
    return datetime.now(SGT)


def parse_slot(slot: str) -> datetime:
    return datetime.strptime(slot, "%Y-%m-%dT%H:%M").replace(tzinfo=SGT)


def resolve(p: str) -> Path:
    path = Path(p)
    return path if path.is_absolute() else (ROOT / path).resolve()


def log(msg: str) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    line = f"[{now_sgt():%Y-%m-%d %H:%M:%S %Z}] {msg}"
    with RUN_LOG.open("a") as f:
        f.write(line + "\n")
    print(line)


def load_queue() -> dict:
    if not QUEUE_FILE.exists():
        return {"pending": [], "posted": [], "failed": []}
    return json.loads(QUEUE_FILE.read_text())


def save_queue(q: dict) -> None:
    tmp = QUEUE_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(q, indent=2, ensure_ascii=False))
    os.replace(tmp, QUEUE_FILE)


def with_lock(fn):
    LOCK_FILE.touch(exist_ok=True)
    fd = os.open(LOCK_FILE, os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        return fn()
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def env_or_dotenv() -> dict:
    env = dict(os.environ)
    dotenv = ROOT / ".env"
    if dotenv.exists():
        for line in dotenv.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env.setdefault(k.strip(), v.strip().strip('"'))
    return env


def append_post_log(entry: dict, permalink: str) -> None:
    if not POST_LOG_MD.exists():
        return
    slot_dt = parse_slot(entry["slot_time_sgt"])
    kind = "Carousel" if entry["type"] == "carousel" else "Single"
    headline = ""
    try:
        cap = resolve(entry["caption_file"]).read_text().strip().splitlines()
        if cap:
            headline = cap[0].strip()
    except Exception:
        pass
    row = (
        f"| {slot_dt:%Y-%m-%d %H:%M} | {kind} | {headline} | "
        f"{permalink} | {entry.get('notes', '')} |"
    )
    with POST_LOG_MD.open("a") as f:
        f.write(row + "\n")


def fetch_permalink(post_id: str) -> str:
    try:
        import urllib.parse
        import urllib.request
        env = env_or_dotenv()
        token = env["IG_ACCESS_TOKEN"]
        url = (
            f"https://graph.facebook.com/v21.0/{post_id}"
            f"?fields=permalink&access_token={urllib.parse.quote(token)}"
        )
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.load(r)
        return data.get("permalink", "")
    except Exception as e:
        log(f"WARN: could not fetch permalink for {post_id}: {e}")
        return ""


def run_single(entry: dict) -> str:
    caption = resolve(entry["caption_file"]).read_text()
    image = str(resolve(entry["image_paths"][0]))
    cmd = [
        sys.executable, str(POST_SINGLE),
        "--image", image,
        "--caption", caption,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=str(ROOT))
    if res.returncode != 0:
        raise RuntimeError(f"post_instagram.py failed: {res.stderr or res.stdout}")
    for line in res.stdout.splitlines():
        if line.startswith("SUCCESS! Post published. ID: "):
            return line.split("ID: ", 1)[1].strip()
    raise RuntimeError("post_instagram.py succeeded but no post ID found in output")


def run_carousel(entry: dict) -> str:
    images = [str(resolve(p)) for p in entry["image_paths"]]
    cmd = [
        sys.executable, str(POST_CAROUSEL),
        "--images", *images,
        "--caption-file", str(resolve(entry["caption_file"])),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=str(ROOT))
    if res.returncode != 0:
        raise RuntimeError(f"post_instagram_carousel.py failed: {res.stderr or res.stdout}")
    for line in res.stdout.splitlines():
        if "published" in line.lower() and "ID:" in line:
            return line.split("ID:", 1)[1].strip()
        if line.startswith("SUCCESS! Carousel published. ID: "):
            return line.split("ID: ", 1)[1].strip()
    tail = "\n".join(res.stdout.splitlines()[-5:])
    raise RuntimeError(f"post_instagram_carousel.py succeeded but no post ID found. tail:\n{tail}")


def run_story(entry: dict) -> str:
    """Publish an IGS (Instagram Story). Caption is ignored by the API for stories."""
    image = str(resolve(entry["image_paths"][0]))
    cmd = [
        sys.executable, str(POST_SINGLE),
        "--image", image,
        "--story",
        "--caption", "",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=str(ROOT))
    if res.returncode != 0:
        raise RuntimeError(f"post_instagram.py --story failed: {res.stderr or res.stdout}")
    for line in res.stdout.splitlines():
        if line.startswith("Story published. ID: "):
            return line.split("ID: ", 1)[1].strip()
    raise RuntimeError("post_instagram.py --story succeeded but no story ID found in output")


def telegram_alert(text: str) -> None:
    """Best-effort Telegram alert. Silently skips if TG_BOT_TOKEN/TG_CHAT_ID unset."""
    import urllib.parse
    import urllib.request
    env = env_or_dotenv()
    token = env.get("TG_BOT_TOKEN") or os.environ.get("TG_BOT_TOKEN")
    chat = env.get("TG_CHAT_ID") or os.environ.get("TG_CHAT_ID")
    if not token or not chat:
        return
    try:
        data = urllib.parse.urlencode({"chat_id": chat, "text": text[:3500]}).encode()
        req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=data)
        urllib.request.urlopen(req, timeout=10).read()
    except Exception as e:
        log(f"WARN: telegram alert failed: {e}")


def process_entry(entry: dict) -> dict:
    log(f"Posting {entry['id']} ({entry['type']}) — notes: {entry.get('notes','')}")
    try:
        if entry["type"] == "single":
            post_id = run_single(entry)
        elif entry["type"] == "carousel":
            post_id = run_carousel(entry)
        elif entry["type"] == "story":
            post_id = run_story(entry)
        else:
            raise ValueError(f"unknown type: {entry['type']}")
        # Stories don't have a public permalink via Graph API; skip fetch
        permalink = "" if entry["type"] == "story" else fetch_permalink(post_id)
        entry["status"] = "posted"
        entry["posted_url"] = permalink or post_id
        entry["posted_at"] = now_sgt().strftime("%Y-%m-%d %H:%M SGT")
        entry["post_id"] = post_id
        append_post_log(entry, permalink or post_id)
        log(f"OK  {entry['id']} -> {permalink or post_id}")
        telegram_alert(f"✅ TRW IG posted: {entry['id']} ({entry['type']})\n{permalink or post_id}")
        # Auto-queue companion IGS for feed posts (10 min after publish)
        if entry["type"] in ("single", "carousel") and not entry.get("is_companion"):
            try:
                _queue_feed_companion_igs(entry)
            except Exception as ce:
                log(f"WARN: companion IGS queue failed for {entry['id']}: {ce}")
        return entry
    except Exception as e:
        entry["status"] = "failed"
        entry["error"] = str(e)[:500]
        entry["attempts"] = entry.get("attempts", 0) + 1
        log(f"ERR {entry['id']}: {e}")
        telegram_alert(
            f"❌ TRW IG FAILED: {entry['id']} ({entry['type']})\n"
            f"slot: {entry.get('slot_time_sgt','?')} SGT\n"
            f"attempts: {entry['attempts']}\n"
            f"error: {str(e)[:400]}"
        )
        return entry


def _queue_feed_companion_igs(parent_entry: dict) -> None:
    """Queue an IGS that promotes the feed post that was just published.

    The companion uses the parent's first image as-is (Story-style 9:16 reframing
    happens in a future renderer pass; for v1 we re-use the cover image at native
    aspect, which Meta will letterbox into 9:16). Posts 10 minutes after parent.
    """
    parent_id = parent_entry["id"]
    companion_id = f"{parent_id}-igs"
    slot = (now_sgt() + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M")
    image = parent_entry["image_paths"][0]  # use cover image for now
    entry = {
        "id": companion_id,
        "slot_time_sgt": slot,
        "type": "story",
        "caption_file": parent_entry["caption_file"],  # ignored by API for stories
        "image_paths": [image],
        "notes": f"Companion IGS for feed post {parent_id}",
        "status": "pending",
        "attempts": 0,
        "is_companion": True,
        "parent_post_id": parent_entry.get("post_id", ""),
    }
    q = load_queue()
    # Avoid duplicate companion if one already exists
    if any(e["id"] == companion_id for e in q["pending"] + q.get("posted", []) + q.get("failed", [])):
        log(f"skip companion: {companion_id} already exists")
        return
    q["pending"].append(entry)
    save_queue(q)
    log(f"queued companion IGS: {companion_id} for {slot} SGT")


def cmd_run() -> int:
    def work():
        q = load_queue()
        now = now_sgt()
        due = []
        keep = []
        for e in q["pending"]:
            slot = parse_slot(e["slot_time_sgt"])
            if slot > now:
                keep.append(e)
                continue
            if now - slot > timedelta(minutes=GRACE_MINUTES):
                e["status"] = "failed"
                e["error"] = "missed_grace_window"
                q["failed"].append(e)
                log(f"SKIP {e['id']} — past {GRACE_MINUTES}-min grace window")
                telegram_alert(
                    f"⏰ TRW IG MISSED: {e['id']} ({e['type']})\n"
                    f"slot: {e['slot_time_sgt']} SGT (past {GRACE_MINUTES}-min grace window)"
                )
                continue
            due.append(e)
        q["pending"] = keep
        save_queue(q)
        return due

    due = with_lock(work)
    if not due:
        log("run: no due posts")
        return 0

    for entry in due:
        processed = process_entry(entry)
        def update():
            q = load_queue()
            bucket = "posted" if processed["status"] == "posted" else "failed"
            q[bucket].append(processed)
            save_queue(q)
        with_lock(update)
    return 0


def cmd_list() -> int:
    q = load_queue()
    print("=== PENDING ===")
    for e in sorted(q["pending"], key=lambda x: x["slot_time_sgt"]):
        print(f"  [{e['slot_time_sgt']} SGT] {e['type']:<8} {e['id']} — {e.get('notes','')}")
    print(f"\n=== POSTED ({len(q['posted'])}) ===")
    for e in q["posted"][-10:]:
        print(f"  {e.get('posted_at','?')} {e['id']} -> {e.get('posted_url','?')}")
    print(f"\n=== FAILED ({len(q['failed'])}) ===")
    for e in q["failed"][-10:]:
        print(f"  {e['slot_time_sgt']} {e['id']} :: {e.get('error','?')}")
    return 0


def cmd_add(args) -> int:
    cap = resolve(args.caption_file)
    if not cap.exists():
        print(f"ERROR: caption file not found: {cap}")
        return 1
    image_paths = [str(args.images[i]) for i in range(len(args.images))]
    for p in image_paths:
        if not resolve(p).exists():
            print(f"ERROR: image not found: {resolve(p)}")
            return 1
    datetime.strptime(args.slot, "%Y-%m-%dT%H:%M")
    if args.type == "story":
        entry_type = "story"
    elif len(image_paths) > 1:
        entry_type = "carousel"
    else:
        entry_type = args.type or "single"
    entry = {
        "id": args.id,
        "slot_time_sgt": args.slot,
        "type": entry_type,
        "caption_file": args.caption_file,
        "image_paths": image_paths,
        "notes": args.notes or "",
        "status": "pending",
        "attempts": 0,
    }
    def work():
        q = load_queue()
        q["pending"] = [e for e in q["pending"] if e["id"] != args.id]
        q["pending"].append(entry)
        save_queue(q)
    with_lock(work)
    print(f"Queued {args.id} for {args.slot} SGT ({entry['type']}, {len(image_paths)} image(s))")
    return 0


def cmd_remove(args) -> int:
    def work():
        q = load_queue()
        before = len(q["pending"])
        q["pending"] = [e for e in q["pending"] if e["id"] != args.id]
        save_queue(q)
        return before - len(q["pending"])
    removed = with_lock(work)
    print(f"Removed {removed} entry(ies) with id={args.id}")
    return 0


def main():
    p = argparse.ArgumentParser(description="TRW Instagram queue runner")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run")
    sub.add_parser("list")
    a = sub.add_parser("add")
    a.add_argument("--id", required=True)
    a.add_argument("--slot", required=True)
    a.add_argument("--caption-file", required=True)
    a.add_argument("--images", nargs="+", required=True)
    a.add_argument("--type", choices=["single", "carousel", "story"], default=None)
    a.add_argument("--notes", default="")
    r = sub.add_parser("remove")
    r.add_argument("--id", required=True)
    args = p.parse_args()
    return {"run": cmd_run, "list": cmd_list,
            "add": lambda: cmd_add(args), "remove": lambda: cmd_remove(args)}[args.cmd]()


if __name__ == "__main__":
    sys.exit(main())
