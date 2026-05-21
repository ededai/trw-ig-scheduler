#!/usr/bin/env python3
"""
TRW News Card Renderer
======================
Renders branded news blog cards by compositing text onto base templates.
No external API calls. Free per run after one-time base template generation.

Base templates (2624×1632 px):
  assets/card-bases/base-coe.png  — dark card + upward bar chart
  assets/card-bases/base-lta.png  — dark card + ERP gantry icon
  assets/card-bases/logo-light.png — TRW horizontal wordmark (white/transparent)

Usage (CLI):
  python3 news_card_renderer.py coe \
      --label "SINGAPORE COE UPDATE" \
      --headline "Cat A COE May 2026" \
      --stat "Up 21% year on year" \
      --out /tmp/coe-card.png

  python3 news_card_renderer.py lta \
      --label "SINGAPORE LTA UPDATE" \
      --headline "ERP 2.0 OBU Now Mandatory" \
      --stat "From 1 Jan 2026" \
      --out /tmp/lta-card.png

Usage (module):
  from news_card_renderer import render_news_card
  path = render_news_card(
      card_type="coe",
      label="SINGAPORE COE UPDATE",
      headline="Cat A COE May 2026",
      stat="Up 21% year on year",
      out_path="/tmp/card.png",
  )
"""
from __future__ import annotations
import argparse
import os
import sys
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).parent / "assets" / "card-bases"

# Card dimensions (matches generated base templates)
W, H = 2624, 1632

# Colour palette
BG       = (36, 40, 52)       # dark card background
ORANGE   = (255, 107, 33)
WHITE    = (255, 255, 255)

# Text layout — left-side text zone, 130px left margin
MARGIN_L = 150        # breathing room from left border

# Per-template config — zones derived from pixel scan of base templates:
#   coe: bar chart leftmost orange at x=1382 → safe zone = 1382-150-92=1140
#   lta: gantry leftmost pixel at x=1427 → safe zone = 1427-150-97=1180
CARD_CONFIG = {
    "coe": {"zone": 1140, "font": 215, "font_sm": 175, "font_xs": 145, "y_shift":  0},
    "lta": {"zone": 1180, "font": 185, "font_sm": 155, "font_xs": 128, "y_shift": 40},
}
CARD_CONFIG_DEFAULT = {"zone": 1100, "font": 200, "font_sm": 165, "font_xs": 135, "y_shift": 0}

# Vertical positions (absolute px on 2624×1632 canvas)
Y_LABEL      = 110             # small eyebrow label (breathing from top border)
Y_HEADLINE   = 260             # large headline starts here (gap below label)
Y_STAT_BASE  = 1120            # minimum stat baseline; renderer uses max(this+y_shift, headline_end+90)
# Logo and cover are baked into base templates — no runtime compositing needed


# ── font helpers ──────────────────────────────────────────────────────────────

def _find_font(bold: bool = True) -> str:
    """Return path to a usable sans-serif TTF, platform-aware."""
    candidates = []
    if bold:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",    # macOS
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Ubuntu
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Ubuntu fallback
        ]
    else:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return ""  # Pillow will use its built-in bitmap font as last resort


def _load(path: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


# ── text wrapping ─────────────────────────────────────────────────────────────

def _wrap_headline(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    """Wrap headline to fit within max_w pixels. No forced merging — returns as many
    lines as natural wrapping produces. Single words that exceed max_w stay on their
    own line (no sub-word splitting). Caller shrinks font if line count is too high."""
    words = text.split()
    lines: list[str] = []
    current = ""
    tmp_draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))

    for word in words:
        test = (current + " " + word).strip()
        bbox = tmp_draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_w:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    return lines or [text]


# ── main renderer ─────────────────────────────────────────────────────────────

def render_news_card(
    card_type: str,
    label: str,
    headline: str,
    stat: str,
    out_path: str | Path,
) -> str:
    """
    Render a news card PNG.

    Args:
        card_type:  "coe" | "lta"
        label:      Small eyebrow text, e.g. "SINGAPORE COE UPDATE"
        headline:   Main headline, e.g. "Cat A COE May 2026"
        stat:       Orange subline, e.g. "Up 21% year on year"
        out_path:   Output PNG path

    Returns:
        Absolute path to the saved PNG.
    """
    card_type = card_type.lower().strip()
    cfg = CARD_CONFIG.get(card_type, CARD_CONFIG_DEFAULT)
    text_zone_w = cfg["zone"]
    y_shift     = cfg["y_shift"]
    base_file = ASSETS / f"base-{card_type}.png"
    if not base_file.exists():
        raise FileNotFoundError(
            f"Base template not found: {base_file}\n"
            f"Available types: {[p.stem.replace('base-','') for p in ASSETS.glob('base-*.png')]}"
        )

    # Load base template (logo + cover already baked in by patch script)
    card = Image.open(base_file).convert("RGBA")
    draw = ImageDraw.Draw(card)

    # 1. Load fonts
    bold_font_path = _find_font(bold=True)
    label_font     = _load(bold_font_path, 68)
    stat_font      = _load(bold_font_path, 88)

    # 4. Draw label (small white caps eyebrow)
    draw.text((MARGIN_L, Y_LABEL + y_shift), label.upper(), font=label_font, fill=WHITE)

    # 5. Draw headline — try font sizes from largest to smallest until all lines fit
    #    within zone AND line count <= 3. Prevents the merged-overflow bug.
    tmp_draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    font_sizes = [cfg["font"], cfg["font_sm"], cfg["font_xs"]]
    headline_font = _load(bold_font_path, font_sizes[0])
    lines = _wrap_headline(headline, headline_font, text_zone_w)
    for fsz in font_sizes[1:]:
        all_fit  = all(tmp_draw.textbbox((0,0), ln, font=headline_font)[2] <= text_zone_w for ln in lines)
        fits_3   = len(lines) <= 3
        if all_fit and fits_3:
            break
        headline_font = _load(bold_font_path, fsz)
        lines = _wrap_headline(headline, headline_font, text_zone_w)

    line_h = int(headline_font.size * 1.1)
    y = Y_HEADLINE + y_shift
    for ln in lines:
        draw.text((MARGIN_L, y), ln, font=headline_font, fill=WHITE)
        y += line_h

    # 6. Draw stat line in orange — shrink font if stat would exceed zone width
    stat_w = tmp_draw.textbbox((0, 0), stat, font=stat_font)[2]
    if stat_w > text_zone_w:
        for sz in range(80, 44, -4):
            sf = _load(bold_font_path, sz)
            if tmp_draw.textbbox((0, 0), stat, font=sf)[2] <= text_zone_w:
                stat_font = sf
                break
    stat_y = max(Y_STAT_BASE + y_shift, y + 90)
    draw.text((MARGIN_L, stat_y), stat, font=stat_font, fill=ORANGE)

    # 7. Save
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    card.convert("RGB").save(str(out), "PNG", optimize=False)
    return str(out.resolve())


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Render a TRW news blog card PNG without any API calls."
    )
    ap.add_argument("card_type", choices=["coe", "lta"],
                    help="Base template to use")
    ap.add_argument("--label",    required=True, help="Small eyebrow label (caps)")
    ap.add_argument("--headline", required=True, help="Main headline text")
    ap.add_argument("--stat",     required=True, help="Orange stat/subline text")
    ap.add_argument("--out",      required=True, help="Output PNG path")
    args = ap.parse_args()

    try:
        path = render_news_card(
            card_type=args.card_type,
            label=args.label,
            headline=args.headline,
            stat=args.stat,
            out_path=args.out,
        )
        print(f"Saved: {path}")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
