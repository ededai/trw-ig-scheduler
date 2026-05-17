#!/usr/bin/env python3
"""Daily Telegram sanity check on the 4 LTA news articles' featured_media.

Why this exists (audit 2026-05-17 fix #7): an unknown WP plugin or hook
has, on at least 5 separate occasions on 2026-05-16, reset featured_media
on the 4 LTA news articles to media id 958 (the legacy oilpour image).
Until we identify the culprit, this script is the safety net.

What it does:
  1. Queries WP REST for each of the 4 articles' current featured_media.
  2. Resolves each to a source_url filename.
  3. Compares against the expected news_b_<pid>_*.png pattern.
  4. If any reverted, auto-re-pins to the correct media id.
  5. Sends a Telegram report to Ed with status + any re-pin actions.

Idempotent. If everything is correct, sends a brief OK ping.
"""
from __future__ import annotations
import base64, json, os
from pathlib import Path
from urllib import request, error, parse

WP_ORIGIN = "https://therightworkshop.com"
HERE = Path(__file__).parent

# Article page id -> expected media id (Direction B thumbnail uploaded
# 2026-05-15). If the news_b_*.png URL filename matches the pattern, the
# state is correct. If featured_media is media 958 (oilpour) or any other
# id whose URL doesn't match, it has reverted.
EXPECTED = {
    6279: {"slug": "erp-2-obu-now-mandatory-key-dates-and-penalties-for-singapore-drivers", "expected_media_id": 6829, "label": "ERP 2 OBU"},
    6199: {"slug": "vep-and-gvp-fees-rise-from-january-2027-for-foreign-vehicles", "expected_media_id": 6835, "label": "VEP & GVP"},
    6193: {"slug": "singapore-ev-licence-plates-lta-and-scdf-begin-design-consultation", "expected_media_id": 6840, "label": "EV plates"},
    6187: {"slug": "singapore-parf-rebate-schedule-and-cap-revised-from-feb-2026", "expected_media_id": 6845, "label": "PARF rebate"},
}


def load_env() -> dict:
    env = {}
    for k in ("WORDPRESS_USERNAME", "WORDPRESS_PASSWORD",
              "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"):
        if os.environ.get(k):
            env[k] = os.environ[k]
    for cand in [
        Path("/Users/admin/the-right-workshop/tools/.env"),
        HERE.parent / "tools" / ".env",
        Path(".env"),
    ]:
        if cand.exists():
            for line in cand.read_text().splitlines():
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    return env


def auth_header(env: dict) -> str:
    return "Basic " + base64.b64encode(
        f"{env['WORDPRESS_USERNAME']}:{env['WORDPRESS_PASSWORD']}".encode()
    ).decode()


def wp_get(env: dict, path: str, params: str = ""):
    url = f"{WP_ORIGIN}/wp-json/wp/v2{path}{params}"
    req = request.Request(url, headers={"Authorization": auth_header(env)})
    try:
        with request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except error.HTTPError as e:
        print(f"  GET {path} -> HTTP {e.code}")
        return None


def wp_post(env: dict, path: str, body: dict) -> bool:
    url = f"{WP_ORIGIN}/wp-json/wp/v2{path}"
    req = request.Request(
        url, data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": auth_header(env), "Content-Type": "application/json"},
    )
    try:
        with request.urlopen(req, timeout=30) as r:
            r.read()
            return True
    except error.HTTPError as e:
        print(f"  POST {path} -> HTTP {e.code}: {e.read().decode()[:200]}")
        return False


def telegram_send(env: dict, text: str) -> bool:
    bot = env.get("TELEGRAM_BOT_TOKEN") or env.get("TG_BOT")
    chat = env.get("TELEGRAM_CHAT_ID") or env.get("TG_CHAT")
    if not bot or not chat:
        print("  TG creds missing — skipping notification")
        return False
    url = f"https://api.telegram.org/bot{bot}/sendMessage"
    data = parse.urlencode({"chat_id": chat, "text": text, "parse_mode": "Markdown"}).encode()
    try:
        with request.urlopen(request.Request(url, data=data), timeout=20) as r:
            r.read()
        print("  TG sent.")
        return True
    except Exception as e:
        print(f"  TG ERR: {e}")
        return False


def main() -> int:
    env = load_env()
    if not env.get("WORDPRESS_USERNAME"):
        print("ABORT: WP creds missing"); return 1

    reverted = []
    ok = []
    for pid, spec in EXPECTED.items():
        page = wp_get(env, f"/pages/{pid}", "?_fields=featured_media")
        fm_id = (page or {}).get("featured_media") or 0
        if fm_id == spec["expected_media_id"]:
            ok.append(spec["label"])
            continue
        # Reverted. Resolve current media URL for the report.
        cur_media = wp_get(env, f"/media/{fm_id}", "?_fields=source_url") if fm_id else None
        cur_url = (cur_media or {}).get("source_url", "(no media set)")
        reverted.append({
            "label": spec["label"], "pid": pid, "slug": spec["slug"],
            "expected": spec["expected_media_id"], "actual": fm_id,
            "actual_url": cur_url,
        })

    if not reverted:
        msg = (
            "TRW Thumb Check\n"
            "All 4 LTA news articles OK.\n"
            f"`{' · '.join(ok)}` Direction B thumbs intact."
        )
        print("All 4 articles OK")
        telegram_send(env, msg)
        return 0

    # Auto-re-pin the reverted ones
    repinned = []
    for r in reverted:
        if wp_post(env, f"/pages/{r['pid']}", {"featured_media": r["expected"]}):
            repinned.append(r)
            print(f"  re-pinned {r['label']} fm={r['expected']}")

    lines = ["TRW Thumb Check — REVERTED", ""]
    for r in reverted:
        fn = (r["actual_url"] or "").split("/")[-1]
        lines.append(f"• {r['label']}: was `{fn[:50]}` (media {r['actual']}), expected `{r['expected']}`")
    if repinned:
        lines.append("")
        lines.append(f"Auto-re-pinned {len(repinned)}/{len(reverted)}. Ed: open /news/ to verify thumbs render correctly.")
    msg = "\n".join(lines)
    print(msg)
    telegram_send(env, msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
