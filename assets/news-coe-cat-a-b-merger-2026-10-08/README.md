# COE Cat A + Cat B merger: Cole news draft + infographic (8 Oct 2026)

Status: DRAFT. Not published to WordPress, not queued in `ig_queue.json`.

| File | What |
|---|---|
| `article.json` | Cole NewsDraft fields (slug, title, thumbnail_title, meta, tags) + sources |
| `body.html` | Article body for `/news/{slug}/` (827 words) |
| `caption.txt` | IG carousel caption |
| `slides/slide_1-5.png` | 1080x1350 infographic carousel (source: `carousels/coe-merger-2026-10-08/slides.html`) |

Mandostack gates run: Cole `style_validator`, `draft_rules.detect_slop` (house rules + structural pass), and `tools/copy_scan.py` + `house_rules.py` on the caption. All clean.
COE premiums and quotas verified against trw-cole `data/coe_history.json` (2026/02/2, 2026/10/1).
Feebate amounts, dates and the feedback link come from news coverage of the LTA consultation; confirm against the LTA paper before publishing.
