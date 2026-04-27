#!/usr/bin/env python3
"""
TRW IG Daily Pre-flight + Telegram Heartbeat.

Runs at 06:00 SGT every morning. Verifies the entire publishing chain is
healthy and pings Ed on Telegram with today's plan + yesterday's results.

Checks:
  1. Repo is PUBLIC (raw.githubusercontent.com responds 200)
  2. Each pending asset for today is reachable via raw URL (HEAD 200, image/*)
  3. IG access token still valid (Graph API /me works)
  4. TG_BOT_TOKEN + TG_CHAT_ID configured and Telegram API reachable

If any check fails: send a FAILURE alert.
Always: send a heartbeat with today's schedule + yesterday's results.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

SGT = ZoneInfo("Asia/Singapore")
ROOT = Path(__file__).parent.resolve()
QUEUE_FILE = ROOT / "ig_queue.json"

# Load .env if present (local Mac dev). On GH Actions, env vars come from secrets.
ENV_FILE = ROOT / ".env"
if ENV_FILE.exists():
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            v = v.strip().strip('"').strip("'")
            os.environ.setdefault(k.strip(), v)

GH_REPO_OWNER = (os.environ.get("GH_REPO_OWNER") or "ededai").strip()
GH_REPO_NAME = (os.environ.get("GH_REPO_NAME") or "trw-ig-scheduler").strip()


def now_sgt():
    return datetime.now(SGT)


def tg(text: str) -> bool:
    token = (os.environ.get("TG_BOT_TOKEN") or "").strip()
    chat = (os.environ.get("TG_CHAT_ID") or "").strip()
    if not token or not chat:
        print("WARN: TG_BOT_TOKEN/TG_CHAT_ID missing — skipping Telegram")
        return False
    try:
        data = urllib.parse.urlencode({"chat_id": chat, "text": text[:3500]}).encode()
        req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=data)
        urllib.request.urlopen(req, timeout=15).read()
        return True
    except Exception as e:
        print(f"telegram failed: {e}")
        return False


def http_status(url: str, method: str = "GET", timeout: int = 15):
    req = urllib.request.Request(url, headers={"User-Agent": "trw-preflight/1.0"}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception as e:
        return None, {"error": str(e)}


def check_repo_public():
    url = f"https://raw.githubusercontent.com/{GH_REPO_OWNER}/{GH_REPO_NAME}/main/README.md"
    status, _ = http_status(url, "HEAD")
    return status == 200, f"raw.githubusercontent.com README: {status}"


def check_ig_token():
    token = (os.environ.get("IG_ACCESS_TOKEN") or "").strip()
    ig_user = (os.environ.get("IG_USER_ID") or "").strip()
    if not token or not ig_user:
        return False, "IG_ACCESS_TOKEN or IG_USER_ID env missing"
    url = f"https://graph.facebook.com/v19.0/{ig_user}?fields=id,username&access_token={urllib.parse.quote(token)}"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            d = json.load(r)
        return True, f"IG token OK (@{d.get('username', '?')})"
    except Exception as e:
        return False, f"IG token check failed: {str(e)[:200]}"


def check_tg():
    token = (os.environ.get("TG_BOT_TOKEN") or "").strip()
    if not token:
        return False, "TG_BOT_TOKEN missing"
    try:
        with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/getMe", timeout=10) as r:
            d = json.load(r)
        return d.get("ok", False), f"Telegram bot @{d.get('result', {}).get('username', '?')}"
    except Exception as e:
        return False, f"Telegram check failed: {str(e)[:200]}"


def check_assets_for_today(queue):
    """For every entry slotted today, HEAD-check the raw URL for each image."""
    today = now_sgt().date().isoformat()
    fails = []
    checked = 0
    for e in queue.get("pending", []):
        if not e["slot_time_sgt"].startswith(today):
            continue
        for path in e["image_paths"]:
            checked += 1
            url = f"https://raw.githubusercontent.com/{GH_REPO_OWNER}/{GH_REPO_NAME}/main/{path}"
            status, headers = http_status(url, "HEAD")
            ct = headers.get("content-type", headers.get("Content-Type", "?"))
            if status != 200 or not str(ct).startswith("image/"):
                fails.append(f"{e['id']} :: {path} -> status={status} ct={ct}")
    if fails:
        return False, f"{checked} assets checked, {len(fails)} broken:\n  " + "\n  ".join(fails)
    return True, f"All {checked} asset URL(s) for today reachable as image/*"


def fmt_today(queue):
    today = now_sgt().date().isoformat()
    rows = sorted(
        [e for e in queue.get("pending", []) if e["slot_time_sgt"].startswith(today)],
        key=lambda x: x["slot_time_sgt"],
    )
    if not rows:
        return "No posts scheduled for today."
    out = []
    for e in rows:
        slot = e["slot_time_sgt"][-5:]
        out.append(f"  {slot} {e['type']:8} {e['id']}")
    return "\n".join(out)


def fmt_yesterday(queue):
    y = (now_sgt() - timedelta(days=1)).date().isoformat()
    posted = [e for e in queue.get("posted", []) if str(e.get("posted_at", "")).startswith(y)]
    failed = [e for e in queue.get("failed", []) if str(e.get("slot_time_sgt", "")).startswith(y)]
    out = []
    out.append(f"Posted: {len(posted)}")
    for e in posted:
        out.append(f"  ✅ {e['id']} -> {e.get('posted_url', e.get('post_id', '?'))}")
    out.append(f"Failed: {len(failed)}")
    for e in failed:
        out.append(f"  ❌ {e['id']} :: {str(e.get('error', '?'))[:120]}")
    return "\n".join(out)


def main():
    queue = json.loads(QUEUE_FILE.read_text()) if QUEUE_FILE.exists() else {"pending": [], "posted": [], "failed": []}

    checks = []
    for name, fn in [
        ("repo_public", check_repo_public),
        ("ig_token", check_ig_token),
        ("telegram", check_tg),
        ("today_assets", lambda: check_assets_for_today(queue)),
    ]:
        ok, msg = fn()
        checks.append((name, ok, msg))
        print(f"[{'OK ' if ok else 'FAIL'}] {name}: {msg}")

    failed = [c for c in checks if not c[1]]
    today_str = now_sgt().strftime("%a %d %b %Y")

    if failed:
        msg = (
            f"❌ TRW IG PRE-FLIGHT FAILED ({today_str} 06:00 SGT)\n\n"
            + "\n".join(f"❌ {n}: {m}" for n, ok, m in checks if not ok)
            + "\n\n--- All checks ---\n"
            + "\n".join(f"{'✅' if ok else '❌'} {n}: {m}" for n, ok, m in checks)
        )
        tg(msg)
        # Exit non-zero so the workflow shows red and you'll see it on GH too
        sys.exit(1)

    msg = (
        f"☀️ TRW IG morning brief ({today_str})\n\n"
        f"--- Today's schedule ---\n{fmt_today(queue)}\n\n"
        f"--- Yesterday ---\n{fmt_yesterday(queue)}\n\n"
        f"All pre-flight checks ✅"
    )
    tg(msg)
    print("Pre-flight passed.")


if __name__ == "__main__":
    main()
