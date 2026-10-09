# TRW Instagram operating plan, from 13 Oct 2026

Written for Ed. This is how we run Instagram with the new pieces: the voice profile, the monthly Phase 2 brief, Reels in the experimental slot, and the credibility set. It replaces nothing in the 9-phase production stack; it tells us what to feed into it and when.

## The loop

| When | What happens | Who | Time |
|---|---|---|---|
| First week of each month | Phase 2 run: collector pulls the watchlist, ranker scores it, I deconstruct the top 20 and write the brief (5 angles, 5 opening lines, a week of idea briefs) | Me | 30 min |
| Batch day, weekly (default Monday) | I build 9 posts from the brief: 7 carousels or singles in canonical modes, 2 Reels in the experimental slots. Captions and Reel lines are written against the voice profile. Preview HTML goes to you | Cole writes and renders, Dom QAs | 2 to 3 hours of my time |
| Same day, evening | You read the preview, edit anything, say go | You | 15 min |
| Daily | The scheduler posts at 12:30, 19:30 and 21:00 SGT; stories as queued | GitHub Actions | 0 |
| Once a month | I read Instagram Insights from your signed-in Chrome tab (view only, no API needed): top posts by saves, reach and profile visits over 30 days. Formats that beat the carousel baseline get promoted; the rest get dropped | Me, with your tab open | 15 min |
| Once a month, when you have an hour | Path A filming at the workshop, 10 clips from the shot list in the brief | You or a mechanic | 1 hour |

## What's new, and what it changes

**Voice profile.** `/Users/admin/the-right-workshop/voice-profile-trw.md`. Every caption and every Reel line gets checked against the snapshot, the signature moves and the never-says list before QA. Writers read it in phase 3 of the stack. Once you send 5 to 10 of your own customer messages, I update it so it sounds like you rather than like us.

**Monthly Phase 2 brief.** `competitor_engine/data/ideas_latest.md`, dated copy alongside. Topics come from what's winning in the niche in the last 60 days plus the credibility set, not from guessing. The 10 Oct run is the first since June.

**Reels.** Two per batch in the experimental slots, hook on screen and spoken in the first 2 seconds, captions throughout. The frame-by-frame pass on the three winning mechanic Reels changed the shape: they run 71 to 163 seconds, one person at a bench, zero cuts, no call to action, and they open by saying the customer's own belief and then turning on it. So the format that wins is you or a mechanic talking to the phone for 45 to 90 seconds with one claim and a turn (Path C). Path B (real workshop photos, slow pan, captions, one voiceover line, 15 to 25 seconds, assembled in Remotion) is the stopgap that starts this week. Path A b-roll clips support both. Promotion to canonical only when saves and profile visits beat the carousel baseline across 2 or 3 runs.

**Credibility set first.** Five topics have never appeared in 238 posted captions: the pre-purchase inspection, the parts tray, the photo before we replace anything over the agreed amount, the drop-off walk-around, moving day. They go ahead of aircon, brakes, tyres and battery, which already have 8 to 25 posts each.

**Watchlist refresh.** Four dormant accounts out, two live SG workshops in (kgcworkshop, dmotorwerkz), plus whatever handles you send. The engine can only learn from accounts that post, and SG workshops mostly don't, which is the opening for TRW.

## What I need from you to start the first batch

1. Batch day: Monday 13 Oct, or another day.
2. OK on the watchlist changes, and 5 SG handles you already follow.
3. The moving-day feed post: Friday 17 Oct before the switch, after the 19th, or not at all.
4. When you can do the one-hour filming session (the shot list is in the brief).
5. Optional but useful: 5 to 10 of your own customer messages or review replies, pasted or screenshotted, for the voice profile.

## Measuring without an API

Instagram gives no API access to insights on this account, so the monthly read happens through your signed-in Chrome tab. I open the professional dashboard, read the 30-day top content by saves and reach, note it in `ig_post_log.md`, and close the tab. Nothing is posted or changed during that read. If you'd rather, a screenshot of the Insights screen once a month does the same job.
