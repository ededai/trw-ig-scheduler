"""Build one contact sheet per mode showing all slides side-by-side."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ASSETS = Path('/Users/admin/the-right-workshop/trw-ig-scheduler/assets')
OUT = Path('/Users/admin/the-right-workshop/trw-ig-scheduler/carousels/contact_sheets')
OUT.mkdir(exist_ok=True)

MODES = [
    # Originally-built 5 prototypes
    ("Mode B — WLD Battery Light", "newseries-wl-mode-b-2026-05-02-11"),
    ("Mode A — ST Three Questions", "newseries-st-mode-a-2026-05-02-15"),
    ("Mode C — CoW Skip the Oil", "newseries-cow-mode-c-2026-05-04-20"),
    ("Mode D — CoW One Year Too Long", "newseries-cow-mode-d-2026-05-06-20"),
    ("Mode E — WLD ABS Off", "newseries-wl-mode-e-2026-05-08-11"),
    # 16 new carousels
    ("Mode B — CoW Brake Fluid $80→$3,400", "newseries-cow-mode-b-2026-05-02-20"),
    ("Mode A — DM What I wish I knew at 23", "newseries-dm-mode-a-2026-05-03-11"),
    ("Mode A — BtB Honda Vezel honest take", "newseries-bbtb-vezel-mode-a-2026-05-03-20"),
    ("Mode C — WLD Check engine $30→$3,000", "newseries-wl-mode-c-2026-05-04-11"),
    ("Mode C — ST Bring receipts walk away clean", "newseries-st-mode-c-2026-05-04-15"),
    ("Mode B — DM Read the dipstick", "newseries-dm-mode-b-2026-05-05-11"),
    ("Mode B — BtB Vezel honest list", "newseries-bbtb-vezel-mode-b-2026-05-05-20"),
    ("Mode D — WLD Drove on red light", "newseries-wl-mode-d-2026-05-06-11"),
    ("Mode D — ST 4-line honest test", "newseries-st-mode-d-2026-05-06-15"),
    ("Mode C — DM On the PIE watch the gauges", "newseries-dm-mode-c-2026-05-07-11"),
    ("Mode C — BtB Find the right Vezel workshop", "newseries-bbtb-vezel-mode-c-2026-05-07-20"),
    ("Mode E — ST Honest vs upsell side by side", "newseries-st-mode-e-2026-05-13-11"),
    ("Mode E — CoW Service interval numbers", "newseries-cow-mode-e-2026-05-13-15"),
    ("Mode D — DM My first car 230k km", "newseries-dm-mode-d-2026-05-13-20"),
    ("Mode D — BtB Vezel notes from workshop floor", "newseries-bbtb-vezel-mode-d-2026-05-14-15"),
    ("Mode E — BtB Vezel spec card", "newseries-bbtb-vezel-mode-e-2026-05-14-20"),
]

THUMB_W = 360   # each slide width
THUMB_H = 450   # each slide height (4:5 ratio)
GAP = 24
HEADER_H = 80
PADDING = 32

for label, slug in MODES:
    src = ASSETS / slug / "slides"
    slide_files = sorted(src.glob("slide_*.png"))
    n = len(slide_files)
    if n == 0:
        print(f"skip {slug} — no slides")
        continue
    # Single row layout
    total_w = PADDING * 2 + n * THUMB_W + (n - 1) * GAP
    total_h = PADDING * 2 + HEADER_H + THUMB_H + 50  # +50 for slide number label
    sheet = Image.new("RGB", (total_w, total_h), (240, 235, 220))
    draw = ImageDraw.Draw(sheet)
    try:
        font_label = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 28)
        font_small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 18)
    except OSError:
        font_label = ImageFont.load_default()
        font_small = ImageFont.load_default()
    draw.text((PADDING, PADDING), label, fill=(20, 20, 20), font=font_label)
    draw.text((PADDING, PADDING + 40), f"{n} slides · {slug}", fill=(120, 120, 120), font=font_small)

    x = PADDING
    y = PADDING + HEADER_H
    for i, sf in enumerate(slide_files, start=1):
        img = Image.open(sf).convert("RGB")
        img = img.resize((THUMB_W, THUMB_H), Image.LANCZOS)
        sheet.paste(img, (x, y))
        # slide number caption
        draw.text((x, y + THUMB_H + 8), f"Slide {i}", fill=(20, 20, 20), font=font_small)
        x += THUMB_W + GAP

    out_path = OUT / f"{slug}_contact.png"
    sheet.save(out_path, "PNG", optimize=True)
    print(f"  built {out_path} ({n} slides)")

print("done.")
