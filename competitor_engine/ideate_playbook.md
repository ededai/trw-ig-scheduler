# Phase 2 — Deconstruct + Ideate Playbook

Turns `data/ranked_latest.json` (this cycle's competitor/overseas winners) into 5 TRW idea briefs ready for Phase 3 generation. Run weekly. Goal is not engagement for its own sake. The goal is content that moves a viewer toward a booking.

## Step A — Deconstruct each top winner
For each top-ranked post, extract:
1. **Hook** — the first line / cover that stops the scroll.
2. **Format** — reel / carousel / single; talking-head / b-roll / graphic.
3. **Pattern** — the transferable structure: anti-overcharge reveal, loss-aversion, DIY-check, myth-bust, price-shock, before/after, model brief, trust/testimonial.
4. **Why it worked** — the trigger: curiosity, loss aversion, save-value, social proof, specificity.
5. **CTA** — the action it drove.

## Step B — Filter for TRW fit
Keep a pattern only if it:
- Fits the honest-mechanic / educational / informative position.
- Can be built with NO workshop footage (carousel, graphic, testimonial).
- Drives business (save -> DM -> booking), not vanity reach.

Drop: exotic-car flexing, pure entertainment, anything that needs video we cannot shoot yet.

## Step C — Map each kept pattern to a TRW idea brief
- Source post (+ its real numbers) so we can measure our version against it later.
- Pattern borrowed.
- TRW topic — specific and SG-relevant.
- Canonical mode (A Editorial Dark, B Cream Magazine, C Poster Bold, D Polaroid Zine, E Spec Sheet, F Receipt, H Diagram, or Voice).
- Hook line.
- Slide structure (cover -> body -> CTA).
- Business CTA (save / DM / book a second opinion).
- Why it works for us.

## Step D — Balance the batch (5 posts/week, Mon-Fri)
Mix lanes so the grid is not repetitive, and rotate modes (no two consecutive the same). Target weekly shape:
- 2 educational (how-to / self-check)
- 1 anti-overcharge or price-shock
- 1 informative (model brief / real cost)
- 1 trust (testimonial reformat)

## Where the intelligence runs
The collect + rank steps are pure Python on a cron (cheap, no LLM). This deconstruct + ideate step runs inside a scheduled Claude Code session (Max plan), not a raw API script. Reason: better judgement, no separate API key or per-call cost, and Ed can steer it. The cron pings "winners ready"; the Claude session produces the briefs below; Ed reviews.
