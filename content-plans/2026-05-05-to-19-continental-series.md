# TRW IG — Continental Car Series (21 posts)

**Author:** Bryan
**Approved by:** Ed (matrix locked 2026-05-05)
**Status:** Plan locked, awaiting approval to author briefs
**Slot window:** May 5-19, mixed across vacant slots in pending queue

---

## Matrix (21 posts)

5 models × 4 angles = 20 + 1 series finale.

| # | Date target | Slot | Series | Model | Angle | Mode |
|---|-------------|------|--------|-------|-------|------|
| 1 | May 6 | 11:00 | Behind the Badge | VW Golf Mk7/7.5 | Driving experience — why SG owners love it | mode-a (editorial-dark) |
| 2 | May 6 | 17:00 | Honest List | VW Golf Mk7/7.5 | Common faults — DSG mechatronic, water pump, coilpacks | mode-c (poster-bold) |
| 3 | May 7 | 11:00 | Hidden Costs | VW Golf Mk7/7.5 | Used buyer's guide — DSG service interval truth | mode-e (spec-sheet) |
| 4 | May 7 | 20:00 | Cost of Waiting | VW Golf Mk7/7.5 | Ignored DSG judder → mechatronic replacement | mode-d (polaroid-zine) |
| 5 | May 8 | 11:00 | Behind the Badge | BMW 3 Series F30/G20 | Driving experience — RWD balance, the hot-hatch killer | mode-b (cream-magazine) |
| 6 | May 8 | 17:00 | Honest List | BMW 3 Series F30/G20 | Common faults — VANOS, oil filter housing leak, EPS rack | mode-c (poster-bold) |
| 7 | May 9 | 11:00 | Hidden Costs | BMW 3 Series F30/G20 | Used buyer's guide — what an N20 owner needs to inspect | mode-e (spec-sheet) |
| 8 | May 9 | 17:00 | Cost of Waiting | BMW 3 Series F30/G20 | Ignored oil filter housing weep → cooked engine | mode-d (polaroid-zine) |
| 9 | May 10 | 11:00 | Behind the Badge | BMW 5 Series F10/G30 | Driving experience — the executive cruiser that drives like a sports sedan | mode-a (editorial-dark) |
| 10 | May 10 | 17:00 | Honest List | BMW 5 Series F10/G30 | Common faults — air suspension (G30), N55 valve cover, electronics | mode-c (poster-bold) |
| 11 | May 11 | 11:00 | Hidden Costs | BMW 5 Series F10/G30 | Used buyer's guide — air suspension is a coin flip | mode-e (spec-sheet) |
| 12 | May 11 | 20:00 | Cost of Waiting | BMW 5 Series F10/G30 | Ignored air suspension warning → S$4-6k repair | mode-d (polaroid-zine) |
| 13 | May 12 | 11:00 | Behind the Badge | Mini Cooper R56/F56 | Driving experience — the SG go-kart with character | mode-b (cream-magazine) |
| 14 | May 12 | 17:00 | Honest List | Mini Cooper R56/F56 | Common faults — timing chain, water pump, thermostat housing | mode-c (poster-bold) |
| 15 | May 13 | 11:00 | Hidden Costs | Mini Cooper R56/F56 | Used buyer's guide — listen for the timing chain rattle | mode-e (spec-sheet) |
| 16 | May 13 | 17:00 | Cost of Waiting | Mini Cooper R56/F56 | Ignored chain rattle → engine job | mode-d (polaroid-zine) |
| 17 | May 14 | 11:00 | Behind the Badge | Mercedes C-Class W205/W206 | Driving experience — the everyday luxury benchmark | mode-a (editorial-dark) |
| 18 | May 14 | 17:00 | Honest List | Mercedes C-Class W205/W206 | Common faults — air-mass meter, transmission conductor plate, 9G ATF | mode-c (poster-bold) |
| 19 | May 15 | 11:00 | Hidden Costs | Mercedes C-Class W205/W206 | Used buyer's guide — service history is non-negotiable | mode-e (spec-sheet) |
| 20 | May 15 | 17:00 | Cost of Waiting | Mercedes C-Class W205/W206 | Ignored conductor plate weep → gearbox fail | mode-d (polaroid-zine) |
| 21 | May 16 | 11:00 | Behind the Badge (finale) | Continental roundup | Buying a Continental in SG — what to know before you sign | mode-b (cream-magazine) |

Mode coverage check: a × 4, b × 4, c × 5, d × 5, e × 4. Spread evenly. No two consecutive posts share a mode.

---

## Slide structure (per carousel, 6 slides default)

Slide 1: Hook cover (model + angle headline + TRW logo bottom-left)
Slide 2: Setup / context (why this matters in SG specifically)
Slide 3: The meat — facts, faults, costs, or driving notes (2-3 specific points)
Slide 4: The meat continued (deepens slide 3)
Slide 5: TRW take — what we'd say to an owner walking in
Slide 6: CTA — "Continental cars repaired right at TRW. Book a check at therightworkshop.com" + DM/booking line

Honest List + Hidden Costs may stretch to 7 slides if fault list demands it. Behind the Badge stays at 6.

---

## Photo strategy

**Tier 1 (stock first per universal rule):**
- Unsplash searches per model: "VW Golf MK7", "BMW F30", "BMW F10", "Mini Cooper", "Mercedes C-Class W205"
- Pexels backup
- Reuse existing P_ENGINE / P_DASH / P_BRAKE / P_NIGHT constants where the shot is generic-mechanic not model-specific

**Tier 2 (Nano Banana fallback):**
- For SG-context shots that stock can't deliver (workshop interior with specific Conti model, SG carplate context)
- Carplate masking mandatory (TRW logo overlay per universal rule)
- Singapore feel mandatory (HDB / SG road / SG workshop backdrop, never generic)
- Save to `assets/nano-banana-generated/instagram/conti-series/`

**Tier 3 (last resort):**
- Generic mode-c poster-bold layouts that don't need a hero photo (type-led)

---

## Caption structure (Ed-approved tone — mechanic-honest, no AI slop, no em dashes)

Hook (1 line) — the model + the angle in plain talk
Setup (2-3 lines) — why SG owners care
Body (4-6 short lines) — the mechanic-honest take, the fault, the cost, the wait
TRW close (1 line) — what we do about it
CTA (1 line) — book / DM / link

Hashtags: `#therightworkshop #singaporecars #continentalcars #[model-tag] #carworkshop #[brand-tag]`

---

## Approvals required before authoring

1. Matrix and mode assignments — approve / change
2. Slide structure default of 6 slides — confirm
3. Photo strategy tiers — confirm
4. Caption structure — confirm

Once Ed signs off → I author all 21 briefs into `canonical_briefs.py`, sourcing photos in parallel, then run `run_canonical.py` to render slides, then Dom runs visual QA on every slide, then I append 21 entries to `ig_queue.json` pending list with the duplicate-post guard.

---

## QA gates before scheduling

- Dom QA every slide for: text-photo alignment, no overflow, font sizes match canonical IG template, no AI slop in copy, no em dashes, carplate masked on every visible plate, brand orange consistent
- Bryan caption review per memory feedback rules
- `verify-before-shipping` skill loaded before any post goes live
- Duplicate-post guard activated (already wired per ig_post_guard.py)
