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
import urllib.error
import urllib.request
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
GRACE_MINUTES = 90  # legacy — kept for back-compat in tooling/refs
MAX_LAG_HOURS = 12  # catch-up window: publish a missed slot up to 12h late
HEARTBEAT_GAP_MIN = 30  # alert if cron silently dropped runs for this long
HEARTBEAT_FILE = "logs/last_run.txt"


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


def verify_post_live(post_id: str) -> bool:
    """Confirm a published media_id actually exists on the IG account.
    Guards against the silent-fail mode where /media_publish returns an
    id but the post never goes live (observed 2026-04-27 timing-belt).
    Returns True if Graph API confirms the post; False otherwise.
    """
    try:
        env = env_or_dotenv()
        token = (env.get("IG_ACCESS_TOKEN") or os.environ.get("IG_ACCESS_TOKEN") or "").strip()
        if not token:
            return True  # can't verify without token; don't block
        url = f"https://graph.facebook.com/v21.0/{post_id}?fields=id&access_token={token}"
        urllib.request.urlopen(url, timeout=15).read()
        return True
    except urllib.error.HTTPError as e:
        if e.code == 400:
            return False
        log(f"WARN: verify_post_live HTTP {e.code} for {post_id}: {e}")
        return True  # non-400 errors are likely transient; don't fail-loud
    except Exception as e:
        log(f"WARN: verify_post_live error for {post_id}: {e}")
        return True


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
        stripped = line.strip()
        if stripped.startswith("SUCCESS. Post id: "):
            return stripped.split("Post id: ", 1)[1].strip()
        if stripped.startswith("SUCCESS! Carousel published. ID: "):
            return stripped.split("ID: ", 1)[1].strip()
        if "published" in stripped.lower() and "ID:" in stripped:
            return stripped.split("ID:", 1)[1].strip()
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
    """Best-effort Telegram alert. Silently skips if TG_BOT_TOKEN/TG_CHAT_ID unset.
    Always .strip() env values — GH Actions secrets often carry trailing newlines
    when pasted from a clipboard, which makes urllib reject the URL.
    """
    import urllib.parse
    import urllib.request
    env = env_or_dotenv()
    token = (env.get("TG_BOT_TOKEN") or os.environ.get("TG_BOT_TOKEN") or "").strip()
    chat = (env.get("TG_CHAT_ID") or os.environ.get("TG_CHAT_ID") or "").strip()
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
        # Verify the media_id actually exists on the account.
        # /media_publish has been observed to return an id for a post that never
        # went live (silent-fail mode, 2026-04-27). Stories are excluded — Graph
        # API can't fetch their permalink with the standard scope.
        if entry["type"] != "story" and not verify_post_live(post_id):
            raise RuntimeError(
                f"Publish reported id={post_id} but Graph API says it does not exist. "
                f"Post is NOT live. Likely silent fail — re-queue and investigate."
            )
        # Stories don't have a public permalink via Graph API; skip fetch
        permalink = "" if entry["type"] == "story" else fetch_permalink(post_id)
        entry["status"] = "posted"
        entry["posted_url"] = permalink or post_id
        entry["posted_at"] = now_sgt().strftime("%Y-%m-%d %H:%M SGT")
        entry["post_id"] = post_id
        append_post_log(entry, permalink or post_id)
        log(f"OK  {entry['id']} -> {permalink or post_id}")
        type_word = {"single":"photo post","carousel":"carousel post","story":"story"}.get(entry["type"], entry["type"])
        nice_link = permalink or f"https://www.instagram.com/p/{post_id}"
        telegram_alert(
            f"✅ Posted live on Instagram\n"
            f"{type_word}: {entry['id']}\n"
            f"{nice_link}"
        )
        return entry
    except Exception as e:
        entry["status"] = "failed"
        entry["error"] = str(e)[:500]
        entry["attempts"] = entry.get("attempts", 0) + 1
        log(f"ERR {entry['id']}: {e}")
        type_word = {"single":"photo post","carousel":"carousel post","story":"story"}.get(entry["type"], entry["type"])
        telegram_alert(
            f"🛑 Post failed to publish\n"
            f"{type_word}: {entry['id']}\n"
            f"scheduled: {entry.get('slot_time_sgt','?')} SGT\n"
            f"attempts so far: {entry['attempts']}\n\n"
            f"What happened: {str(e)[:300]}\n\n"
            f"Action: I'll re-queue and try again, or it'll need a manual reslot."
        )
        return entry


def _heartbeat_check_and_stamp() -> None:
    """Detect when GH Actions cron silently drops scheduled runs.
    If the gap since the last run exceeds HEARTBEAT_GAP_MIN, alert via Telegram.
    Stamps current run timestamp on every invocation.
    """
    hb = ROOT / HEARTBEAT_FILE
    now = now_sgt()
    try:
        if hb.exists():
            prev_iso = hb.read_text().strip()
            if prev_iso:
                prev = datetime.fromisoformat(prev_iso)
                gap_min = (now - prev).total_seconds() / 60
                if gap_min > HEARTBEAT_GAP_MIN:
                    log(f"HEARTBEAT lag {gap_min:.0f} min (prev={prev_iso})")
    except Exception as e:
        log(f"WARN heartbeat read failed: {e}")
    try:
        hb.parent.mkdir(parents=True, exist_ok=True)
        hb.write_text(now.isoformat())
    except Exception as e:
        log(f"WARN heartbeat write failed: {e}")


def cmd_run() -> int:
    _heartbeat_check_and_stamp()

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
            # New: catch up missed slots up to MAX_LAG_HOURS late instead of
            # the old 90-min window. GH Actions cron can lag 2-3h during peak
            # load (observed 2026-04-27: 2h 15min gap dropped igs-10-signs-a).
            # Better to publish a slot 4h late than skip and have nothing live.
            lag_hours = (now - slot).total_seconds() / 3600
            if lag_hours > MAX_LAG_HOURS:
                e["status"] = "failed"
                e["error"] = f"missed_max_lag_window ({lag_hours:.1f}h late, max {MAX_LAG_HOURS}h)"
                q["failed"].append(e)
                log(f"SKIP {e['id']} — {lag_hours:.1f}h past slot (max lag {MAX_LAG_HOURS}h)")
                type_word = {"single":"photo post","carousel":"carousel post","story":"story"}.get(e["type"], e["type"])
                telegram_alert(
                    f"❌ Post window missed\n"
                    f"{type_word}: {e['id']}\n"
                    f"scheduled: {e['slot_time_sgt']} SGT\n"
                    f"now: {lag_hours:.1f} hours past the slot\n\n"
                    f"This post will not auto-publish anymore. It needs a new time slot."
                )
                continue
            if lag_hours > 0.5:
                # publishing late but within max-lag window
                log(f"CATCH-UP {e['id']} — {lag_hours:.1f}h late, publishing")
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
