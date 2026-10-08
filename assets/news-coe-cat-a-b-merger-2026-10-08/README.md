# COE Cat A + Cat B merger: plain-words explainer + infographics (8 Oct 2026)

Status: DRAFT. Not published to WordPress, not queued in `ig_queue.json`.

| File | What |
|---|---|
| `preview-desktop.pdf`, `preview-mobile.pdf` | The article rendered inside the live TRW news page design |
| `featured.png` | Hero / thumbnail card (Cole Direction D, LTA NEWS) |
| `article.json` | Cole NewsDraft fields (slug, title, thumbnail_title, meta, tags), publish notes, sources |
| `body.html` | Article body for `/news/{slug}/` (~460 words): simple news explainer with 3 inline infographics |
| `infographics/coe-merger-infographic-1, 3, 4.png` | Web infographics in the TRW site palette, 1800px wide (source: `carousels/coe-merger-2026-10-08/web_infographics.html`) |
| `slides/slide_1-5.png` | 1080x1350 IG carousel (source: `carousels/coe-merger-2026-10-08/slides.html`) |
| `caption.txt` | IG carousel caption |

Mandostack gates run: Cole `style_validator`, `draft_rules.detect_slop` (house rules + structural pass), and `tools/copy_scan.py` + `house_rules.py`. All clean.
Every COE premium and quota verified against trw-cole `data/coe_history.json` (LTA DataMall), Jun 2025 to 7 Oct 2026.
Feebate amounts, Cat E options, quotes and expert views come from news coverage of the LTA consultation (ST via syndicated excerpts, Mothership, AsiaOne, Goody Feed, Red Hot). Confirm against the LTA paper before publishing.
