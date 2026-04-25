# TRW Instagram Scheduler

Cloud-hosted IG queue runner for **@therightworkshop**. Cron lives on GitHub Actions, so Ed's Mac can be off and posts still go out.

## How it works

1. Posts are queued in `ig_queue.json` (slot time in SGT, type, caption file, image paths).
2. GitHub Actions runs `ig_queue.py run` every 15 min.
3. Any post whose `slot_time_sgt` has passed (and is within the 90-min grace window) is published via `post_instagram.py` (single) or `post_instagram_carousel.py` (carousel).
4. The runner commits the updated queue + log back to the repo.

## Files

- `ig_queue.py` — runner (subcommands: `run`, `list`, `add`, `remove`)
- `ig_queue.json` — queue state
- `post_instagram.py`, `post_instagram_carousel.py` — Meta Graph API publishing scripts
- `ig_post_log.md` — append-only post history
- `assets/<post-id>/` — slides + caption.txt for each scheduled post
- `.github/workflows/ig-cron.yml` — cron + manual-dispatch workflow

## Required secrets

Set in GitHub repo → Settings → Secrets and variables → Actions:

- `IG_USER_ID` — Instagram Business account ID
- `IG_ACCESS_TOKEN` — long-lived Meta access token
- `IMGBB_API_KEY` — used by `post_instagram.py` to host single images

## Queueing a post (local workflow)

```bash
git pull
python3 ig_queue.py add \
  --id my-post-2026-05-01 \
  --slot 2026-05-01T19:30 \
  --caption-file assets/my-post-2026-05-01/caption.txt \
  --images assets/my-post-2026-05-01/slide1.png assets/my-post-2026-05-01/slide2.png \
  --notes "What this post is about"
git add assets/my-post-2026-05-01 ig_queue.json
git commit -m "queue: my-post-2026-05-01"
git push
```

The next cron tick on or after the slot will publish it.

## Constraints

- Meta Graph API does **not** support `scheduled_publish_time` for IG. The runner publishes at slot time; it doesn't pre-schedule on Meta's side.
- Meta Graph API does **not** support deleting published IG media. Deletions must happen in the IG app.
- IG Content Publishing API: 25 publishes per IG account per 24h.
- All `slot_time_sgt` values are Asia/Singapore time regardless of runner TZ.
