"""Master contact sheet showing all 21 carousels.
Slide 1 = original slide.png. Slides 2..N = slides/slide_N.png.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ASSETS = Path('/Users/admin/the-right-workshop/trw-ig-scheduler/assets')
OUT = Path('/Users/admin/the-right-workshop/trw-ig-scheduler/carousels/contact_sheets/MASTER_all_21.png')

CAROUSELS = [
    ("Mode B · WLD Battery Light", "newseries-wl-mode-b-2026-05-02-11"),
    ("Mode A · ST Three Questions", "newseries-st-mode-a-2026-05-02-15"),
    ("Mode B · CoW Brake Fluid $80→$3,400", "newseries-cow-mode-b-2026-05-02-20"),
    ("Mode A · DM What I wish I knew at 23", "newseries-dm-mode-a-2026-05-03-11"),
    ("Mode A · BtB Honda Vezel honest take", "newseries-bbtb-vezel-mode-a-2026-05-03-20"),
    ("Mode C · WLD Check engine $30→$3,000", "newseries-wl-mode-c-2026-05-04-11"),
    ("Mode C · ST Bring receipts walk away clean", "newseries-st-mode-c-2026-05-04-15"),
    ("Mode C · CoW Skip the Oil Kill the Engine", "newseries-cow-mode-c-2026-05-04-20"),
    ("Mode B · DM Read the dipstick", "newseries-dm-mode-b-2026-05-05-11"),
    ("Mode B · BtB Vezel honest list", "newseries-bbtb-vezel-mode-b-2026-05-05-20"),
    ("Mode D · WLD Drove on red light", "newseries-wl-mode-d-2026-05-06-11"),
    ("Mode D · ST 4-line honest test", "newseries-st-mode-d-2026-05-06-15"),
    ("Mode D · CoW One Year Too Long", "newseries-cow-mode-d-2026-05-06-20"),
    ("Mode C · DM On the PIE watch the gauges", "newseries-dm-mode-c-2026-05-07-11"),
    ("Mode C · BtB Find the right Vezel workshop", "newseries-bbtb-vezel-mode-c-2026-05-07-20"),
    ("Mode E · WLD ABS off does not mean brakes off", "newseries-wl-mode-e-2026-05-08-11"),
    ("Mode E · ST Honest vs upsell side by side", "newseries-st-mode-e-2026-05-13-11"),
    ("Mode E · CoW Service interval numbers", "newseries-cow-mode-e-2026-05-13-15"),
    ("Mode D · DM My first car 230k km", "newseries-dm-mode-d-2026-05-13-20"),
    ("Mode D · BtB Vezel notes from workshop floor", "newseries-bbtb-vezel-mode-d-2026-05-14-15"),
    ("Mode E · BtB Vezel spec card", "newseries-bbtb-vezel-mode-e-2026-05-14-20"),
]

THUMB_W = 220; THUMB_H = 275; GAP_X = 12; GAP_Y = 32; LABEL_H = 24; MARGIN = 28; ROW_LABEL_H = 26
max_slides = 9
total_w = MARGIN * 2 + max_slides * THUMB_W + (max_slides - 1) * GAP_X
total_h = MARGIN * 2 + len(CAROUSELS) * (THUMB_H + LABEL_H + ROW_LABEL_H + GAP_Y) - GAP_Y + 80

sheet = Image.new("RGB", (total_w, total_h), (245, 240, 232))
draw = ImageDraw.Draw(sheet)
try:
    font_title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 30)
    font_row = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 18)
    font_small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 13)
except OSError:
    font_title = ImageFont.load_default(); font_row = ImageFont.load_default(); font_small = ImageFont.load_default()

draw.text((MARGIN, 16), "TRW IG Carousels — Master Preview · 21 carousels · May 2-14 · slide 1 = approved cover · slides 2-N = canonical-CSS expansion", fill=(20, 20, 20), font=font_title)

y = 80
for label, slug in CAROUSELS:
    draw.text((MARGIN, y), label, fill=(20, 20, 20), font=font_row)
    y += ROW_LABEL_H
    src = ASSETS / slug
    cover = src / "slide.png"
    expansions = sorted((src / "slides").glob("slide_*.png")) if (src / "slides").exists() else []
    all_slides = []
    if cover.exists():
        all_slides.append(("1 (cover)", cover))
    for sp in expansions:
        idx = sp.stem.replace("slide_", "")
        all_slides.append((idx, sp))
    x = MARGIN
    for tag, sf in all_slides:
        try:
            img = Image.open(sf).convert("RGB")
            img.thumbnail((THUMB_W, THUMB_H), Image.LANCZOS)
            box = Image.new("RGB", (THUMB_W, THUMB_H), (255, 255, 255))
            box.paste(img, ((THUMB_W - img.width) // 2, (THUMB_H - img.height) // 2))
            sheet.paste(box, (x, y))
            draw.text((x, y + THUMB_H + 2), tag, fill=(80, 80, 80), font=font_small)
        except Exception:
            draw.text((x + 8, y + THUMB_H // 2), "missing", fill=(180, 80, 80), font=font_small)
        x += THUMB_W + GAP_X
    y += THUMB_H + LABEL_H + GAP_Y

OUT.parent.mkdir(parents=True, exist_ok=True)
sheet.save(OUT, "PNG", optimize=True)
print(f"  built {OUT} ({len(CAROUSELS)} carousels, size {total_w}x{total_h})")
